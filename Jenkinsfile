pipeline{
    agent any

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
    }
}