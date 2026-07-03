pipeline{
    agent any

    tools {
        maven 'maven'
        jdk 'java-17'
    }

    environment{
        IMAGE_NAME = 'snakegame:${GIT_COMMIT}'
    }

    stages{
        stage('compile'){
            steps{
                sh '''
                echo 'Compiling the code...'
                mvn compile
                '''
            }
        }

        stage('build'){
            steps{
                sh '''
                echo 'Building the code...'
                mvn clean install
                '''
            }
        }

        stage('docker build'){
            steps{
                sh '''
                printenv
                echo 'Building the docker image...'
                docker build -t ${IMAGE_NAME} .
                '''
            }
        }
    }
}