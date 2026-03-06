pipeline {
    agent any 

    tools {
        jdk 'java-17'
        maven 'maven'
    }

    environment {
        IMAGE_NAME   = "manojkrishnappa/microdegree-game-app:${GIT_COMMIT}"
        AWS_REGION   = "us-east-2"
        CLUSTER_NAME = "itkannadigaru-cluster"
        NAMESPACE    = "microdegree"
    }

    stages {

        stage('Git Checkout') {
            steps {
                git url: 'https://github.com/ManojKRISHNAPPA/SnakeGame.git', branch: 'main'
            }
        }

        stage('Compile') {
            steps {
                sh '''
                    mvn compile
                '''
            }
        }

        stage('Packaging') {
            steps {
                sh '''
                    mvn clean package
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    printenv
                    docker build -t ${IMAGE_NAME} .
                '''
            }
        }

        stage('Login to DockerHub') {
            steps {
                script {
                    withCredentials([
                        usernamePassword(
                            credentialsId: 'docker-hub-creds',
                            usernameVariable: 'DOCKER_USERNAME',
                            passwordVariable: 'DOCKER_PASSWORD'
                        )
                    ]) {
                        sh '''
                        echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
                        '''
                    }
                }
            }
        }

        stage('Push to DockerHub') {
            steps {
                sh '''
                    docker push ${IMAGE_NAME}
                '''
            }
        }

        stage('Update kubeconfig') {
            steps {
                sh '''
                aws eks update-kubeconfig \
                --region ${AWS_REGION} \
                --name ${CLUSTER_NAME}
                '''
            }
        }

        stage('Deploy to EKS') {
            steps {
                withKubeConfig(
                    caCertificate: '',
                    clusterName: 'itkannadigaru-cluster',
                    contextName: '',
                    credentialsId: 'kube',
                    namespace: 'microdegree',
                    restrictKubeConfigAccess: false,
                    serverUrl: 'https://8D99702D402132411F7EA231534E3166.gr7.us-west-2.eks.amazonaws.com'
                ) {
                    sh '''
                    sed -i "s|replace|${IMAGE_NAME}|g" deployment.yml
                    kubectl apply -f deployment.yml -n ${NAMESPACE}
                    '''
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                withKubeConfig(
                    caCertificate: '',
                    clusterName: 'itkannadigaru-cluster',
                    contextName: '',
                    credentialsId: 'kube',
                    namespace: 'microdegree',
                    restrictKubeConfigAccess: false,
                    serverUrl: 'https://8D99702D402132411F7EA231534E3166.gr7.us-west-2.eks.amazonaws.com'
                ) {
                    sh '''
                    kubectl get pods -n ${NAMESPACE}
                    kubectl get svc -n ${NAMESPACE}
                    '''
                }
            }
        }

    }
}