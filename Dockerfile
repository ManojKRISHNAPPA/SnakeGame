FROM eclipse-temurin:17-jdk

RUN useradd -m appuser

WORKDIR /app
COPY target/gameapp-1.0.0.jar app.jar
RUN chown -R appuser:appuser .

USER appuser

EXPOSE 8080

CMD ["java","-jar","app.jar"]


