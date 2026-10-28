"""Generate the editable native JMeter plan; Groovy contains only fixture/assertion glue."""
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
def prop(parent,name,value,tag='stringProp'):
    x=E.SubElement(parent,tag,{'name':name});x.text=str(value);return x
def element(tree,tag,name,gui,test=None):
    x=E.SubElement(tree,tag,{'guiclass':gui,'testclass':test or tag,'testname':name,'enabled':'true'})
    h=E.SubElement(tree,'hashTree');return x,h
def groovy(tree,name,file,tag='JSR223Sampler'):
    x,h=element(tree,tag,name,'TestBeanGUI')
    prop(x,'scriptLanguage','groovy');prop(x,'filename','jmeter/'+file);prop(x,'cacheKey','true');return x,h
def headers(tree,json=False):
    x,h=element(tree,'HeaderManager','CSRF / content type','HeaderPanel')
    c=E.SubElement(x,'collectionProp',{'name':'HeaderManager.headers'})
    for name,value in [('X-CSRF-Token','${csrf}')]+([('Content-Type','application/json')] if json else []):
        e=E.SubElement(c,'elementProp',{'name':name,'elementType':'Header'});prop(e,'Header.name',name);prop(e,'Header.value',value)
def http(tree,name,path,method,body=None,file=None):
    x,h=element(tree,'HTTPSamplerProxy',name,'HttpTestSampleGui')
    prop(x,'HTTPSampler.domain','${__P(host,127.0.0.1)}');prop(x,'HTTPSampler.port','${__P(port,40797)}');prop(x,'HTTPSampler.protocol','http')
    prop(x,'HTTPSampler.path','${__P(basePath,/movie-lab/api)}/'+path);prop(x,'HTTPSampler.method',method)
    prop(x,'HTTPSampler.connect_timeout','10000');prop(x,'HTTPSampler.response_timeout','40000')
    prop(x,'HTTPSampler.follow_redirects','false','boolProp');prop(x,'HTTPSampler.use_keepalive','true','boolProp')
    args=E.SubElement(x,'elementProp',{'name':'HTTPsampler.Arguments','elementType':'Arguments','guiclass':'HTTPArgumentsPanel','testclass':'Arguments','enabled':'true'})
    c=E.SubElement(args,'collectionProp',{'name':'Arguments.arguments'})
    if body is not None:
        e=E.SubElement(c,'elementProp',{'name':'','elementType':'HTTPArgument'});prop(e,'HTTPArgument.always_encode','false','boolProp');prop(e,'Argument.value',body);prop(e,'Argument.metadata','=')
        prop(x,'HTTPSampler.postBodyRaw','true','boolProp')
    if file:
        prop(x,'HTTPSampler.DO_MULTIPART_POST','true','boolProp')
        fs=E.SubElement(x,'elementProp',{'name':'HTTPsampler.Files','elementType':'HTTPFileArgs'})
        c=E.SubElement(fs,'collectionProp',{'name':'HTTPFileArgs.files'})
        e=E.SubElement(c,'elementProp',{'name':file,'elementType':'HTTPFileArg'});prop(e,'File.path',file);prop(e,'File.paramname','file');prop(e,'File.mimetype','application/json')
    headers(h,json=body is not None)
    return x,h
root=E.Element('jmeterTestPlan',{'version':'1.2','properties':'5.0','jmeter':'5.6.3'})
tree=E.SubElement(root,'hashTree'); plan,pt=element(tree,'TestPlan','Lab2 concurrent authenticated users','TestPlanGui')
prop(plan,'TestPlan.serialize_threadgroups','true','boolProp')
args=E.SubElement(plan,'elementProp',{'name':'TestPlan.user_defined_variables','elementType':'Arguments'});E.SubElement(args,'collectionProp',{'name':'Arguments.arguments'})
group,gt=element(pt,'ThreadGroup','${__P(scenario,C03)}','ThreadGroupGui')
prop(group,'ThreadGroup.on_sample_error','stoptest')
controller=E.SubElement(group,'elementProp',{'name':'ThreadGroup.main_controller','elementType':'LoopController','guiclass':'LoopControlPanel','testclass':'LoopController','enabled':'true'})
prop(controller,'LoopController.continue_forever','false','boolProp');prop(controller,'LoopController.loops','1')
prop(group,'ThreadGroup.num_threads','${__P(threads,2)}');prop(group,'ThreadGroup.ramp_time','1')
cookies,ch=element(gt,'CookieManager','Independent session per thread','CookiePanel');E.SubElement(cookies,'collectionProp',{'name':'CookieManager.cookies'});prop(cookies,'CookieManager.clearEachIteration','false','boolProp')
groovy(gt,'Load private credentials','init.groovy')
x,h=http(gt,'Login','auth','POST','${loginBody}');groovy(h,'Extract CSRF','login.groovy','JSR223PostProcessor')
loop,lt=element(gt,'LoopController','Fresh target per round','LoopControlPanel');prop(loop,'LoopController.loops','${__P(rounds,20)}');prop(loop,'LoopController.continue_forever','false','boolProp')
groovy(lt,'Prepare shared fixture','prepare.groovy')
def condition(tree,name,expression):
    x,h=element(tree,'IfController',name,'IfControllerPanel');prop(x,'IfController.condition',expression);prop(x,'IfController.useExpression','true','boolProp');return h
rd=condition(lt,'Read initial version','${hasRead}');x,h=http(rd,'Read same target version','${readPath}','GET');groovy(h,'Check initial version','read.groovy','JSR223PostProcessor')
x,h=groovy(lt,'Bounded rendezvous','barrier.groovy');timer,th=element(h,'SyncTimer','Synchronizing Timer','TestBeanGUI');prop(timer,'groupSize','${__P(threads,2)}');prop(timer,'timeoutInMs','20000','longProp')
crud=condition(lt,'CRUD or special operation','${isCrud}');x,h=http(crud,'${__P(scenario)} target','${targetPath}','${targetMethod}','${targetBody}');groovy(h,'Business status and raw result','record.groovy','JSR223PostProcessor')
upload=condition(lt,'Multipart import','${isUpload}');x,h=http(upload,'${__P(scenario)} import','imports','POST',file='${uploadFile}');groovy(h,'Business status and raw result','record.groovy','JSR223PostProcessor')
E.indent(root,space='  ')
(ROOT/'jmeter/lab2-concurrency.jmx').write_bytes(E.tostring(root,encoding='utf-8',xml_declaration=True))
