import java.io.File;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.stream.Collectors;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.*;
import org.semanticweb.owlapi.formats.RDFXMLDocumentFormat;
import org.semanticweb.owlapi.profiles.OWL2DLProfile;
import org.semanticweb.owlapi.util.*;
import org.semanticweb.HermiT.Reasoner;

/** Uses the exact OWLAPI and HermiT JARs installed with Protégé, offline. */
public class VerifyOntology {
    static final String NS = "https://example.org/lol-ontology#";
    static final OWLDataFactory D = OWLManager.getOWLDataFactory();
    static OWLNamedIndividual individual(String s) { return D.getOWLNamedIndividual(IRI.create(NS+s)); }
    static OWLClass cls(String s) { return D.getOWLClass(IRI.create(NS+s)); }
    static OWLObjectProperty prop(String s) { return D.getOWLObjectProperty(IRI.create(NS+s)); }
    static void check(boolean value, String message, StringBuilder log) {
        log.append((value ? "PASS " : "FAIL ") + message + "\n");
        if (!value) throw new AssertionError(log.toString());
    }
    public static void main(String[] args) throws Exception {
        File source = new File(args[0]);
        Path out = Paths.get(args[1]);
        Path ontologyOut = out.resolve("ontologies");
        Path verificationOut = out.resolve("verification");
        Files.createDirectories(ontologyOut);
        Files.createDirectories(verificationOut);
        String variant = source.getName().contains("full") ? "full" : "demo";
        OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
        OWLOntology ontology = manager.loadOntologyFromOntologyDocument(source);
        StringBuilder log = new StringBuilder("Source: " + source.getCanonicalPath() + "\nHermiT: " +
            Reasoner.class.getPackage().getImplementationVersion() + "\n");
        var profile = new OWL2DLProfile().checkOntology(ontology);
        check(profile.isInProfile(), "OWL 2 DL profile " + profile.getViolations(), log);
        OWLReasoner reasoner = new Reasoner.ReasonerFactory().createReasoner(ontology);
        check(reasoner.isConsistent(), "Ontology is consistent", log);
        reasoner.precomputeInferences(InferenceType.CLASS_HIERARCHY, InferenceType.CLASS_ASSERTIONS,
                                     InferenceType.OBJECT_PROPERTY_ASSERTIONS);
        check(reasoner.getUnsatisfiableClasses().getEntitiesMinusBottom().isEmpty(), "No unsatisfiable named classes", log);
        Set<String> matches = reasoner.getInstances(cls("SupportControlMage"), false).getFlattened().stream()
            .map(i -> i.getIRI().getShortForm()).collect(Collectors.toCollection(TreeSet::new));
        check(matches.equals(new TreeSet<>(Arrays.asList("Karma", "Lux", "Morgana"))),
              "Inferred SupportControlMage = " + matches, log);
        check(!ontology.containsAxiom(D.getOWLClassAssertionAxiom(cls("SupportControlMage"), individual("Lux"))),
              "Target class is not pre-asserted for Lux", log);
        for (String champion : Arrays.asList("Lux", "Morgana", "Karma")) {
            check(reasoner.getObjectPropertyValues(individual(champion+"_Q"), prop("isAbilityOf"))
                .containsEntity(individual(champion)), "Inverse ownership: " + champion+"_Q isAbilityOf "+champion, log);
            check(reasoner.getObjectPropertyValues(individual(champion), prop("canApplyMechanic"))
                .containsEntity(individual("Shield")), "Property chain: " +champion+" canApplyMechanic Shield", log);
        }
        check(!reasoner.isEntailed(D.getOWLObjectPropertyAssertionAxiom(prop("hasTargetType"),
                individual("Karma_W_Heal_Self"), individual("Ally"))), "Self-heal is not inferred as ally healing", log);
        check(!reasoner.isEntailed(D.getOWLObjectPropertyAssertionAxiom(prop("hasTargetType"),
                individual("Morgana_R_MovementSpeedBoost_Self"), individual("Ally"))), "Self speed boost stays separate from ally effects", log);
        if (variant.equals("full")) {
            check(!reasoner.isEntailed(D.getOWLClassAssertionAxiom(cls("SupportControlMage"), individual("Aatrox"))),
                  "Unannotated Aatrox is not returned as a proven match (open world)", log);
        }
        OWLOntology materialized = manager.createOntology(ontology.getAxioms(), IRI.create("https://example.org/lol-ontology/inferred/"+variant));
        List<InferredAxiomGenerator<? extends OWLAxiom>> generators = Arrays.asList(
            new InferredClassAssertionAxiomGenerator(), new InferredPropertyAssertionGenerator());
        new InferredOntologyGenerator(reasoner, generators).fillOntology(D, materialized);
        manager.saveOntology(materialized, new RDFXMLDocumentFormat(),
            IRI.create(ontologyOut.resolve("lol_"+variant+"_inferred.owl").toUri()));
        log.append("Asserted axioms: " + ontology.getAxiomCount() + "\nMaterialized axioms: " + materialized.getAxiomCount() + "\n");
        reasoner.dispose();

        // Mutation checks demonstrate that the query depends on both target and condition structure.
        OWLOntology negative = manager.createOntology(ontology.getAxioms());
        manager.removeAxiom(negative, D.getOWLObjectPropertyAssertionAxiom(prop("hasTargetType"),
            individual("Lux_W_Shield_Ally"), individual("Ally")));
        manager.addAxiom(negative, D.getOWLObjectPropertyAssertionAxiom(prop("hasTargetType"),
            individual("Lux_W_Shield_Ally"), individual("Self")));
        OWLReasoner negativeReasoner = new Reasoner.ReasonerFactory().createReasoner(negative);
        check(negativeReasoner.isConsistent() && !negativeReasoner.getInstances(cls("SupportControlMage"), false)
            .containsEntity(individual("Lux")), "Mutation: replacing Lux's ally shield with self shield removes Lux from results", log);
        negativeReasoner.dispose();
        manager.removeOntology(negative);

        OWLOntology bad = manager.createOntology(ontology.getAxioms());
        manager.addAxiom(bad, D.getOWLClassAssertionAxiom(cls("Ability"), individual("Lux")));
        OWLReasoner badReasoner = new Reasoner.ReasonerFactory().createReasoner(bad);
        check(!badReasoner.isConsistent(), "Mutation: Champion/Ability disjointness catches mis-typed Lux", log);
        badReasoner.dispose();
        Files.writeString(verificationOut.resolve("hermit_"+variant+"_verification.txt"), log.toString(), StandardCharsets.UTF_8);
        System.out.print(log);
    }
}
