FROM maven:3.9.9-eclipse-temurin-17 AS build
WORKDIR /workspace
COPY pom.xml .
COPY src src
RUN mvn -B package -DskipTests
FROM payara/micro:6.2025.1
COPY --from=build /workspace/target/movie-lab.war /opt/payara/deployments/movie-lab.war
CMD ["--deploy", "/opt/payara/deployments/movie-lab.war", "--noCluster"]
