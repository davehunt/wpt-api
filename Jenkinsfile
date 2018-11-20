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
      steps {
        sh 'python ./create_dashboards.py'
      }
    }
  }
}
