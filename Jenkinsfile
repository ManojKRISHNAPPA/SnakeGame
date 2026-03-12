pipeline{
    agent any

    tools {
        jdk 'java-17'
        maven 'maven'
    }
    stages{
    //    stage('Git Checkout') {
    //         steps {
    //             git url: 'https://github.com/ManojKRISHNAPPA/SnakeGame.git', branch: 'main'
    //         }
    //     }

        stage('Compile') {
            steps {
                sh '''
                    mvn compile
                '''
            }
        }

        stage('Test & coverage') {
            steps {
                sh '''
                    mvn clean test jacoco:report
                '''
            }

            post {
                always {
                    jacoco(
                        execPattern: 'target/jacoco.exec',
                        classPattern: 'target/classes',
                        sourcePattern: 'src/main/java',
                        exclusionPattern: ''
                    )
                }
            }
        }

        // stage('SonarQube'){
        //     steps{
        //         sh '''
        //             mvn sonar:sonar \
        //             -Dsonar.projectKey=snake-game \
        //             -Dsonar.host.url=http://18.237.61.251:9000 \
        //             -Dsonar.login=925337beed5be219a08790270383b1becf1c2c37
        //         '''
        //     }
        // }

        stage('Sonar-qube-auth'){
            steps{
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        mvn clean package org.sonarsource.scanner.maven:sonar-maven-plugin:sonar
                    '''
                    }
            }
        }

    }
}