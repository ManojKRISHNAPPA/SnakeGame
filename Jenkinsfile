pipeline{
    agent any 

    tools {
        jdk 'java-17'
        maven 'maven'
    }

    environment {
        IAMAGE_NAME = "manojkrishnappa/microdegree-game-app:${GIT_COMMIT}"
        AWS_REGION =  "us-east-2"
        CLUSTER_NAME = "itkannadigaru-cluster"
        NAMESPACE = "microdegree"
    }    



    stages{
        stage('Git-Checkout'){
            steps{
                git url: 'https://github.com/ManojKRISHNAPPA/SnakeGame.git', branch: 'main'
            }
        }

        stage('compile'){
            steps{
                sh '''
                    mvn compile
                '''
            }
        }
        stage('packging'){
            steps{
                sh '''
                    mvn clean package
                '''
            }
        }
        stage('Docker build'){
            steps{
                sh '''
                    printenv
                    docker build -t ${IAMAGE_NAME} .
                '''
            }
        }

    }
}