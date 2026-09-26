# CI/CD Pipeline

船廠研發團隊部署至遠端艦隊。

## 目錄

1. [簡介](#簡介)
2. [工具與技術](#工具與技術)
3. [Pipeline 流程](#pipeline-流程)
4. [Code Freeze](#code-freeze)
5. [Jenkins Pipeline](#jenkins-pipeline)

---

## 簡介

## 工具與技術

- 版本控制與協作（Git、GitHub）
- 容器化與編排（Docker、Kubernetes）
- 基礎設施與組態管理（Terraform、Ansible）
- 監控與視覺化（Prometheus、Grafana）
- 持續整合與持續部署（Jenkins）

## Pipeline 流程

> Build once, deploy many times

Code Freeze 後只做一次 `docker.build`，正式 Release 以這份映像為準，之後各環境都部署同一份，一路 Promotion 到 PRD，不再重新建置。

```mermaid
flowchart TD
    subgraph ci["持續整合"]
        direction LR
        build[Build] --> test[Test]
    end

    subgraph devqa["開發與測試環境"]
        direction LR
        dev[Deploy DEV] --> qa[Deploy QA]
    end

    subgraph rc["Code Freeze / Release Candidate（RC）"]
        direction LR
        freeze[Code Freeze] --> docker["docker.build<br/>Build once · my-app:rc-tag"]
    end

    subgraph preprod["驗證環境 · 同一映像"]
        direction LR
        staging[Deploy Staging] --> uat[Deploy UAT]
    end

    subgraph release["正式發布 · 同一映像 Promotion"]
        direction LR
        approval1{"Approval #1<br/>Deploy Canary?"} --> canary[Canary Deploy]
        canary --> monitor["Monitor / Test"]
        monitor --> approval2{"Approval #2<br/>Deploy to PRD?"}
        approval2 --> prd[PRD Full Deploy]
    end

    ci --> devqa
    devqa --> rc
    rc --> preprod
    preprod --> release

    classDef ciNode fill:#bfdbfe,stroke:#2563eb,color:#1e3a8a
    classDef devqaNode fill:#a5f3fc,stroke:#0891b2,color:#164e63
    classDef rcNode fill:#fde68a,stroke:#d97706,color:#78350f
    classDef preprodNode fill:#ddd6fe,stroke:#7c3aed,color:#4c1d95
    classDef releaseNode fill:#bbf7d0,stroke:#16a34a,color:#14532d
    classDef approvalNode fill:#fecaca,stroke:#dc2626,color:#7f1d1d
    classDef prdNode fill:#16a34a,stroke:#14532d,color:#ffffff,stroke-width:2px

    class build,test ciNode
    class dev,qa devqaNode
    class freeze,docker rcNode
    class staging,uat preprodNode
    class canary,monitor releaseNode
    class approval1,approval2 approvalNode
    class prd prdNode

    style ci fill:#eff6ff,stroke:#2563eb,color:#1e3a8a
    style devqa fill:#ecfeff,stroke:#0891b2,color:#164e63
    style rc fill:#fffbeb,stroke:#d97706,color:#78350f
    style preprod fill:#f5f3ff,stroke:#7c3aed,color:#4c1d95
    style release fill:#f0fdf4,stroke:#16a34a,color:#14532d
```

## Code Freeze

每週固定一次 Release，Code Freeze 是為了決定這次 Release 的內容


假設這週要發布 `v2.5.0`：

```mermaid
flowchart TD
    freeze[Code Freeze] --> tag["Git Tag: v2.5.0-rc.1"]
    tag --> docker["docker.build<br/>Build once"]
    docker --> image["Docker Image<br/>my-app:2.5.0-rc.1"]
    subgraph promotion["deploy many times：同一映像一路 Promotion"]
        direction LR
        staging[Staging] --> uat[UAT]
        uat --> canary[Canary]
        canary --> prd[PRD]
    end
    image --> promotion
    promotion --> release["正式 Release：v2.5.0<br/>沿用 rc 映像，不再重新建置"]

    classDef rcNode fill:#fde68a,stroke:#d97706,color:#78350f
    classDef imageNode fill:#fed7aa,stroke:#c2410c,color:#7c2d12
    classDef preprodNode fill:#ddd6fe,stroke:#7c3aed,color:#4c1d95
    classDef canaryNode fill:#bbf7d0,stroke:#16a34a,color:#14532d
    classDef prdNode fill:#16a34a,stroke:#14532d,color:#ffffff,stroke-width:2px
    classDef releaseNode fill:#166534,stroke:#14532d,color:#ffffff,stroke-width:2px

    class freeze,tag,docker rcNode
    class image imageNode
    class staging,uat preprodNode
    class canary canaryNode
    class prd prdNode
    class release releaseNode

    style promotion fill:#f0fdf4,stroke:#16a34a,color:#14532d
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

        stage('Docker Build') {
            steps {
                sh 'docker build -t my-app:${TAG} .'
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
