# CI/CD Pipeline

船廠研發團隊部署至遠端艦隊。

## 簡介

## 工具與技術

- 版本控制與協作（Git、GitHub）
- 容器化與編排（Docker、Kubernetes）
- 基礎設施與組態管理（Terraform、Ansible）
- 監控與視覺化（Prometheus、Grafana）
- 持續整合與持續部署（Jenkins）

## Pipeline 流程（放階段架構圖）

```
Build
  ↓
Test
  ↓
Deploy DEV
  ↓
Deploy QA
  ↓
──────────────
  Code Freeze
  Release Candidate（RC）
──────────────
  ↓
Deploy Staging
  ↓
Deploy UAT
  ↓
┌─────────────────┐
│ Approval #1     │
│ Deploy Canary?  │
└────────┬────────┘
         ↓
   Canary Deploy
         ↓
   Monitor / Test
         ↓
┌─────────────────┐
│ Approval #2     │
│ Deploy to PRD?  │
└────────┬────────┘
         ↓
   PRD Full Deploy
```

## Code Freeze

每週固定一次 Release，Code Freeze 是為了決定這次 Release 的內容


假設這週要發布 `v2.5.0`：

```
Code Freeze
      ↓
Git Tag: v2.5.0-rc.1
      ↓
Build
      ↓
Docker Image:
my-app:2.5.0-rc.1
      ↓
Staging
```

## Jenkins Pipeline

### Multi-stage Pipeline

```
pipeline {
    agent any

    stages {

        stage('Build') {
            steps {
                sh 'npm install'
                sh 'npm run build'
                echo 'Building...'
            }
        }

        stage('Test') {
            steps {
                sh 'npm test'
            }
        }

        stage('Deploy DEV') {
            steps {
                sh './deploy.sh dev'
            }
        }

        stage('Deploy QA') {
            steps {
                sh './deploy.sh qa'
            }
        }

        stage('Deploy Staging') {
            steps {
                sh './deploy.sh staging'
            }
        }

        stage('Deploy UAT') {
            steps {
                sh './deploy.sh uat'
            }
        }

        stage('Approval - Canary') {
            steps {
                input message: 'Approve Canary Deployment?'
            }
        }

        stage('Canary Deploy') {
            steps {
                sh './deploy.sh canary'
            }
        }

        stage('Approval - Production') {
            steps {
                input message: 'Approve Full Production Deployment?'
            }
        }

        stage('Deploy PRD') {
            steps {
                sh './deploy.sh prd'
            }
        }
    }
}
```
