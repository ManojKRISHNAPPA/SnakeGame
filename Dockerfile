FROM eclipse-temurin:17-jdk


RUN useradd -m appuser

WORKDIR /app

COPY target/*.jar app.jar

USER appuser

RUN chown appuser:appuser .

EXPOSE 8080

CMD ["java", "-jar", "app.jar"]