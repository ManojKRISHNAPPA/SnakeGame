pipeline {
    agent any

    tools{
        maven 'maven'
        jdk 'java-17'
    }
    environment{
        IMAGE_NAME = "manojkrishnappa/snakegame:${GIT_COMMIT}"
        AWS_REGION = "ap-northeast-1"
        CLUSTER_NAME = "shab-cluster"
    }

    stages{
        stage('checkout'){
            steps{
                git branch:'md-devsecops', url: 'https://github.com/ManojKRISHNAPPA/SnakeGame.git'
            }
        }

        stage('compile'){
            steps{
                sh '''
                    mvn clean compile
                '''
            }
        }

        stage('build stage'){
            steps{
                sh '''
                    mvn clean install
                '''
            }
        }

        stage('docker build'){
            steps{
                sh '''
                    docker build -t ${IMAGE_NAME} .
                '''
            }
        }

        stage('Login to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'docker-hub-cred',
                    usernameVariable: 'DOCKER_USERNAME',
                    passwordVariable: 'DOCKER_PASSWORD'
                )]) {
                    sh "echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin"
                }
            }
        }
        stage('uploading docker image to dockerhub'){
            steps{
                sh '''
                    docker push ${IMAGE_NAME}
                '''
            }
        }
    }

}
