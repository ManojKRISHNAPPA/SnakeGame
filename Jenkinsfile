pipeline{
    agent any

    tools {
        maven 'maven'
        jdk 'java-17'
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
                echo 'Building the docker image...'
                docker build -t snakegame:1.0 .
                '''
            }
        }
    }
}