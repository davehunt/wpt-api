#!/usr/bin/env groovy

pipeline {
  agent none
  options {
    timestamps()
    timeout(time: 15, unit: 'MINUTES')
  }
  stages {
    stage('Create dashboards in Datadog') {
      agent {
        dockerfile {
          args '--net host'
        }
      }
      environment {
        DATADOG_API_KEY = credentials("DATADOG_API_KEY")
      }
      steps {
        sh 'python ./create_dashboards.py'
      }
    }
  }
}
