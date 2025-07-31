# 🏠 Fridoma Project
## House Price Prediction with MLOps Practices

---

## 🎯 Introduction

Fridoma is a comprehensive MLOps project that demonstrates how to build, deploy, and monitor machine learning models in production. The project focuses on predicting house prices using real estate data while implementing industry-standard MLOps practices.

This end-to-end solution showcases the complete machine learning lifecycle - from data ingestion and model training to deployment and continuous monitoring. Built on AWS cloud infrastructure, Fridoma provides a scalable, reliable, and cost-effective approach to ML model management.

**Why Fridoma?**
• Demonstrates real-world MLOps implementation
• Provides hands-on experience with modern ML tools
• Shows how to build production-ready ML systems
• Implements best practices for model governance

---

## 📋 Project Overview

• **End-to-end MLOps pipeline** for house price prediction
• **Automated workflows** from data processing to model deployment
• **Real-time inference** with serverless architecture
• **Continuous monitoring** for model performance and data drift
• **A/B testing capabilities** for model comparison
• **User-friendly interface** for seamless interaction

---

## 🔧 Pipelines Setup

### MLOps Server (EC2 Instance)
**Two containerized services:**

**ZenML Container**
• ML pipeline orchestrator
• Data cleaning pipeline
• Feature engineering pipeline  
• Model training pipeline

**MLflow Container**
• Model evaluation and comparison
• Model registry and versioning
• Experiment tracking and metrics

**Storage Integration**
• Connected to Amazon S3 for model artifacts
• Centralized storage for all ML assets

---

## 🖥️ Frontend App

### React-based User Interface
• **Technology**: React.js
• **Hosting**: AWS S3 Static Website Hosting
• **Purpose**: Allow users to interact with prediction platform
• **Features**: 
  - House price prediction requests
  - Real-time results display
  - User feedback collection

---

## ⚡ Inference Service

### Serverless Architecture
**API Gateway**
• Request routing and management
• Rate limiting and security

**Lambda Functions**
• **Prediction Lambda**: 
  - Handles model prediction requests
  - Logs predictions to DynamoDB
• **Feedback Lambda**: 
  - Collects user feedback
  - Stores feedback data

**DynamoDB**
• Stores prediction logs
• Manages user feedback data
• Real-time data access

---

## 🔄 A/B Testing & Rollback

### Traffic Splitting Logic
• **Round-robin algorithm** splits traffic between two models
• **Configuration-driven** A/B testing modes:
  - **A/B Mode**: Serves two models simultaneously
  - **Default Mode**: Serves single stable model

### Rollback Capabilities
• **Quick rollback** to previous stable model version
• **Configuration-based** model switching
• **Zero-downtime** deployments

---

## 📊 ML Monitoring

### Key Monitoring Areas

**Data Drift Detection**
• Monitors changes in input data distribution
• Alerts when new data differs significantly from training data
• Helps identify when model retraining is needed

**Model Performance Tracking**
• Monitors prediction accuracy over time
• Tracks model response times and error rates
• Compares performance between different model versions

### Monitoring Infrastructure
**Dockerized Monitoring App**
• **Streamlit**: Web application framework for dashboard
• **EvidentlyAI**: Advanced ML monitoring and drift detection
• **Real-time dashboards** for model health visualization
• **Automated alerts** for performance degradation

---

## 🏗️ Architecture Summary

```
Frontend (React/S3) → API Gateway → Lambda Functions → Models
                                        ↓
                                   DynamoDB Logs
                                        ↓
                              Monitoring Dashboard
                                   (Streamlit)
```

**Key Benefits:**
• **Scalable**: Serverless architecture handles varying loads
• **Cost-effective**: Pay-per-use pricing model
• **Reliable**: Automated monitoring and rollback capabilities
• **User-friendly**: Simple interface for end users