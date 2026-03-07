# Implementation Plan: AI-Driven Circular Waste Intelligence System

## Overview

This implementation plan breaks down the AI-Driven Circular Waste Intelligence System into phased, incremental tasks. The system integrates computer vision for waste classification, time series forecasting for waste generation prediction, route optimization using reinforcement learning, an on-premise LLM-powered admin dashboard, and a citizen incentive tracker.

The implementation follows a phased approach:
- Phase 1: Foundation and infrastructure setup
- Phase 2: Computer Vision module for waste classification
- Phase 3: Time Series Forecasting module
- Phase 4: Route Optimization engine
- Phase 5: LLM-powered Admin Dashboard (on-premise)
- Phase 6: Citizen Incentive Tracker
- Phase 7: Integration and deployment

Each task references specific requirements from the requirements document for traceability.

## Tasks

### Phase 1: Foundation and Infrastructure Setup

- [ ] 1. Set up project structure and development environment
  - Create Python project with FastAPI backend structure
  - Set up virtual environment and dependency management (Poetry or pip-requirements)
  - Configure Docker containers for development
  - Set up PostgreSQL database with TimescaleDB extension
  - Configure Redis for caching
  - Create directory structure for ML models, services, and APIs
  - _Requirements: 6.1, 5.6_

- [ ] 2. Initialize database schema and core models
  - [ ] 2.1 Create database migration framework (Alembic)
    - Set up Alembic configuration
    - Create initial migration structure
    - _Requirements: 6.1_
  
  - [ ] 2.2 Implement core data models
    - Create SQLAlchemy models for WasteClassification, WasteForecast, OptimizedRoute, CitizenIncentive, CollectionPoint
    - Implement validation rules for each model
    - Add database indexes for performance
    - _Requirements: 4.1, 4.2, 4.3, 4.5_
  
  - [ ]* 2.3 Write unit tests for data models
    - Test model validation rules
    - Test database constraints
    - _Requirements: 5.6_

- [ ] 3. Set up API gateway and authentication
  - [ ] 3.1 Create FastAPI application with basic routing
    - Initialize FastAPI app with CORS middleware
    - Set up API versioning structure
    - Configure logging and error handling
    - _Requirements: 4.4, 5.4_
  
  - [ ] 3.2 Implement authentication and authorization
    - Create JWT-based authentication system
    - Implement role-based access control (RBAC) for admin, operator, citizen roles
    - Hash passwords using bcrypt
    - _Requirements: 5.4_
  
  - [ ]* 3.3 Write unit tests for authentication
    - Test JWT token generation and validation
    - Test RBAC permissions
    - _Requirements: 5.4, 5.6_

- [ ] 4. Checkpoint - Ensure foundation is working
  - Verify database connections and migrations work
  - Verify API authentication endpoints are functional
  - Ensure all tests pass, ask the user if questions arise

### Phase 2: Computer Vision Module for Waste Classification

- [ ] 5. Prepare computer vision infrastructure
  - [ ] 5.1 Set up ML model registry and versioning
    - Configure MLflow for model tracking
    - Create model storage structure
    - Implement model versioning system
    - _Requirements: 4.1, 5.6_
  
  - [ ] 5.2 Create image preprocessing pipeline
    - Implement image resizing, normalization, and augmentation functions
    - Create preprocessing utilities for YOLO input format (640x640)
    - Handle various image formats and lighting conditions
    - _Requirements: 4.1_
  
  - [ ]* 5.3 Write unit tests for preprocessing
    - Test image transformations
    - Test edge cases (corrupted images, wrong formats)
    - _Requirements: 4.1, 5.6_

- [ ] 6. Implement waste detection and classification
  - [ ] 6.1 Create ComputerVisionModule class
    - Implement YOLO model loading and initialization
    - Create detect_waste() method for object detection
    - Implement confidence threshold filtering (≥0.5)
    - Support GPU and CPU inference modes
    - _Requirements: 4.1, 3.1.1_
  
  - [ ] 6.2 Implement waste category classification
    - Create WasteCategory enum (organic, plastic, paper, metal, glass, e_waste, hazardous, mixed)
    - Implement classification logic to map YOLO detections to waste categories
    - Calculate percentage composition from detections
    - _Requirements: 4.1, 3.1.1_
  
  - [ ] 6.3 Implement volume estimation
    - Create calculate_waste_volume() method using camera calibration
    - Estimate volume from 2D bounding boxes
    - Validate volume estimates are physically plausible
    - _Requirements: 4.1, 3.1.1_
  
  - [ ]* 6.4 Write property test for classification determinism
    - **Property 9.1.2: Classification results shall be deterministic for identical input images**
    - **Validates: Requirements 9.1.2**
  
  - [ ]* 6.5 Write unit tests for CV module
    - Test detection with sample images
    - Test category mapping accuracy
    - Test volume estimation calculations
    - _Requirements: 3.1.1, 5.6_

- [ ] 7. Implement waste classification service
  - [ ] 7.1 Create WasteClassificationService API
    - Implement POST /classify endpoint for single image classification
    - Implement GET /collection-points/{id}/stats for aggregated statistics
    - Store classification results in PostgreSQL
    - _Requirements: 4.1, 3.1.1_
  
  - [ ] 7.2 Implement IoT camera stream processing
    - Set up Kafka consumer for camera feeds
    - Implement frame skipping logic (process every 3rd frame)
    - Handle concurrent streams from multiple cameras
    - _Requirements: 3.1.2, 5.1_
  
  - [ ] 7.3 Add model hot-swapping capability
    - Implement update_model() method for zero-downtime model updates
    - Version control for models
    - _Requirements: 4.1, 3.1.1_
  
  - [ ]* 7.4 Write integration tests for classification service
    - Test end-to-end classification flow
    - Test concurrent camera feed processing
    - _Requirements: 3.1.1, 3.1.2_

- [ ] 8. Checkpoint - Verify CV module is functional
  - Test classification with sample images
  - Verify classification accuracy meets ≥85% threshold
  - Ensure all tests pass, ask the user if questions arise

### Phase 3: Time Series Forecasting Module

- [ ] 9. Prepare forecasting infrastructure
  - [ ] 9.1 Set up TimescaleDB for time series data
    - Create hypertables for waste generation data
    - Configure data retention policies
    - Set up continuous aggregates for performance
    - _Requirements: 4.2, 6.1_
  
  - [ ] 9.2 Create feature engineering pipeline
    - Implement extract_features() for time series windows
    - Add external feature integration (weather API, holiday calendar)
    - Create feature normalization and scaling
    - _Requirements: 4.2, 3.2.1_
  
  - [ ]* 9.3 Write unit tests for feature engineering
    - Test feature extraction with sample data
    - Test external API integrations
    - _Requirements: 4.2, 5.6_

- [ ] 10. Implement forecasting models
  - [ ] 10.1 Create TimeSeriesForecastingModule class
    - Implement LSTM model architecture using TensorFlow/PyTorch
    - Implement Prophet model as alternative
    - Create model training pipeline with validation
    - _Requirements: 4.2, 3.2.1_
  
  - [ ] 10.2 Implement prediction with confidence intervals
    - Create predict() method for 7-day and 30-day forecasts
    - Calculate confidence intervals (95%)
    - Implement uncertainty quantification
    - _Requirements: 4.2, 3.2.1_
  
  - [ ] 10.3 Implement anomaly detection
    - Create detect_anomalies() method for unusual patterns
    - Set threshold at 30% deviation from predictions
    - Generate alerts for anomalies
    - _Requirements: 4.2, 3.2.2_
  
  - [ ]* 10.4 Write property test for non-negative predictions
    - **Property 9.2.1: Predicted waste volume shall always be non-negative**
    - **Validates: Requirements 9.2.1**
  
  - [ ]* 10.5 Write property test for category sum consistency
    - **Property 9.2.2: Sum of category-wise predictions shall equal total predicted volume**
    - **Validates: Requirements 9.2.2**
  
  - [ ]* 10.6 Write unit tests for forecasting module
    - Test LSTM and Prophet models with sample data
    - Test confidence interval calculations
    - Test anomaly detection logic
    - _Requirements: 3.2.1, 3.2.2, 5.6_

- [ ] 11. Implement forecasting service
  - [ ] 11.1 Create ForecastingService API
    - Implement GET /forecasts/ward/{ward_id} endpoint
    - Implement POST /forecasts/generate for manual forecast triggers
    - Store forecasts in TimescaleDB
    - _Requirements: 4.2, 3.2.1_
  
  - [ ] 11.2 Set up automated forecast generation
    - Create cron scheduler for daily forecast jobs
    - Implement weekly model retraining pipeline
    - Handle forecast failures and retries
    - _Requirements: 4.2, 3.2.1_
  
  - [ ] 11.3 Implement forecast accuracy tracking
    - Create evaluate_accuracy() method (MAPE, RMSE, MAE)
    - Store accuracy metrics for monitoring
    - Generate accuracy reports
    - _Requirements: 4.2, 3.2.1_
  
  - [ ]* 11.4 Write integration tests for forecasting service
    - Test end-to-end forecast generation
    - Test automated scheduling
    - Test accuracy evaluation
    - _Requirements: 3.2.1, 3.2.2_

- [ ] 12. Checkpoint - Verify forecasting module is functional
  - Test forecast generation for sample wards
  - Verify forecast accuracy meets ≤15% error margin
  - Ensure all tests pass, ask the user if questions arise

### Phase 4: Route Optimization Engine

- [ ] 13. Prepare route optimization infrastructure
  - [ ] 13.1 Set up map data and routing engine
    - Integrate with mapping service API (Google Maps/OpenStreetMap)
    - Load Delhi road network data
    - Create distance and time calculation utilities
    - _Requirements: 4.3, 6.2_
  
  - [ ] 13.2 Create state representation for RL agent
    - Implement build_state_representation() for collection points and trucks
    - Encode spatial, temporal, and capacity features
    - Normalize state vectors
    - _Requirements: 4.3, 3.3.1_
  
  - [ ]* 13.3 Write unit tests for state representation
    - Test state encoding with sample data
    - Test feature normalization
    - _Requirements: 4.3, 5.6_

- [ ] 14. Implement RL-based route optimization
  - [ ] 14.1 Create RouteOptimizationModule class
    - Implement RL agent architecture (DQN or PPO)
    - Create policy network for route generation
    - Implement value network for route evaluation
    - _Requirements: 4.3, 3.3.1_
  
  - [ ] 14.2 Implement route generation and evaluation
    - Create optimize_routes() method using RL policy
    - Calculate route metrics (distance, time, emissions)
    - Implement capacity and time window constraints
    - _Requirements: 4.3, 3.3.1_
  
  - [ ] 14.3 Implement RL training pipeline
    - Create reward function (minimize emissions + time)
    - Implement experience replay buffer
    - Create training loop with policy updates
    - _Requirements: 4.3, 3.3.1_
  
  - [ ]* 14.4 Write property test for route completeness
    - **Property 9.3.1: Optimized route shall visit all required collection points exactly once**
    - **Validates: Requirements 9.3.1**
  
  - [ ]* 14.5 Write property test for route optimality
    - **Property 9.3.2: Total route distance shall be ≤ distance of any manually created route**
    - **Validates: Requirements 9.3.2**
  
  - [ ]* 14.6 Write unit tests for route optimization
    - Test route generation with sample data
    - Test constraint satisfaction
    - Test emissions calculations
    - _Requirements: 3.3.1, 5.6_

- [ ] 15. Implement route optimization service
  - [ ] 15.1 Create RouteOptimizationService API
    - Implement POST /optimize-routes endpoint
    - Implement GET /routes/{route_id} for route details
    - Implement PUT /routes/{route_id}/update for dynamic adjustments
    - Store routes in PostgreSQL
    - _Requirements: 4.3, 3.3.1_
  
  - [ ] 15.2 Implement real-time route adjustment
    - Integrate with traffic data APIs
    - Implement dynamic re-routing logic
    - Handle route updates and notifications to drivers
    - _Requirements: 4.3, 3.3.2_
  
  - [ ] 15.3 Implement route performance tracking
    - Track actual vs predicted metrics
    - Store route execution data for RL training
    - Generate route performance reports
    - _Requirements: 4.3, 3.3.1_
  
  - [ ]* 15.4 Write integration tests for route service
    - Test end-to-end route optimization
    - Test dynamic re-routing
    - Test performance tracking
    - _Requirements: 3.3.1, 3.3.2_

- [ ] 16. Checkpoint - Verify route optimization is functional
  - Test route generation for sample collection points
  - Verify emissions reduction meets ≥20% target
  - Ensure all tests pass, ask the user if questions arise

### Phase 5: LLM-Powered Admin Dashboard (On-Premise)

- [ ] 17. Set up on-premise LLM infrastructure
  - [ ] 17.1 Deploy Llama 3.1 using Ollama or vLLM
    - Install Ollama or vLLM on government servers
    - Download and configure Llama 3.1 8B model
    - Set up model serving endpoint (local API)
    - Configure GPU acceleration if available
    - _Requirements: 4.4, 5.4_
  
  - [ ] 17.2 Deploy Mistral 7B as fallback option
    - Download and configure Mistral 7B model
    - Set up model switching logic
    - Test inference performance for both models
    - _Requirements: 4.4, 5.4_
  
  - [ ]* 17.3 Write unit tests for LLM deployment
    - Test model loading and inference
    - Test model switching
    - Test inference latency
    - _Requirements: 4.4, 5.6_

- [ ] 18. Implement LLM insights engine
  - [ ] 18.1 Create LLMInsightsEngine class
    - Implement initialization with Ollama/vLLM backend
    - Create classify_intent() method for query classification
    - Implement retrieve_relevant_data() for data fetching
    - _Requirements: 4.4, 3.4.1_
  
  - [ ] 18.2 Implement insight generation
    - Create build_prompt() method with context injection
    - Implement generate_insight() using on-premise LLM
    - Add response caching in Redis
    - Support Hindi and English languages
    - _Requirements: 4.4, 3.4.1_
  
  - [ ] 18.3 Implement visualization suggestions
    - Create suggest_visualizations() method
    - Map query intents to appropriate chart types
    - Generate visualization configurations
    - _Requirements: 4.4, 3.4.1_
  
  - [ ]* 18.4 Write unit tests for LLM insights engine
    - Test intent classification
    - Test prompt building
    - Test insight generation
    - Test caching behavior
    - _Requirements: 3.4.1, 5.6_

- [ ] 19. Implement dashboard service and API
  - [ ] 19.1 Create DashboardService API
    - Implement POST /insights/query for natural language queries
    - Implement GET /insights/history for query history
    - Implement GET /dashboard/metrics for real-time KPIs
    - _Requirements: 4.4, 3.4.1_
  
  - [ ] 19.2 Implement automated reporting
    - Create report generation pipeline (daily, weekly, monthly)
    - Generate PDF and Excel exports
    - Include visualizations in reports
    - _Requirements: 4.4, 3.4.2_
  
  - [ ] 19.3 Implement conversation context management
    - Store conversation history for follow-up questions
    - Implement context-aware query processing
    - Handle multi-turn conversations
    - _Requirements: 4.4, 3.4.1_
  
  - [ ]* 19.4 Write integration tests for dashboard service
    - Test end-to-end query processing
    - Test report generation
    - Test conversation context
    - _Requirements: 3.4.1, 3.4.2_

- [ ] 20. Build React admin dashboard UI
  - [ ] 20.1 Create dashboard layout and navigation
    - Set up React project with TypeScript
    - Create responsive layout with sidebar navigation
    - Implement authentication flow
    - _Requirements: 4.4, 5.5_
  
  - [ ] 20.2 Implement real-time metrics display
    - Create KPI cards for key metrics
    - Implement real-time data updates using WebSockets
    - Add charts for waste trends, route performance, forecasts
    - _Requirements: 4.4, 3.4.1_
  
  - [ ] 20.3 Implement natural language query interface
    - Create chat-style query input
    - Display LLM-generated insights
    - Render suggested visualizations
    - Support Hindi and English
    - _Requirements: 4.4, 3.4.1_
  
  - [ ] 20.4 Implement report viewing and export
    - Create report viewer with filters
    - Add PDF and Excel export buttons
    - Display historical reports
    - _Requirements: 4.4, 3.4.2_
  
  - [ ]* 20.5 Write UI tests for dashboard
    - Test component rendering
    - Test user interactions
    - Test data visualization
    - _Requirements: 3.4.1, 5.6_

- [ ] 21. Checkpoint - Verify LLM dashboard is functional
  - Test natural language queries with on-premise LLM
  - Verify no data leaves government network
  - Verify dashboard loads in <3 seconds
  - Ensure all tests pass, ask the user if questions arise

### Phase 6: Citizen Incentive Tracker

- [ ] 22. Implement incentive tracking backend
  - [ ] 22.1 Create IncentiveTrackerService class
    - Implement record_action() for logging citizen actions
    - Create verify_segregation() using CV module
    - Implement calculate_tier() for citizen tiers (Bronze/Silver/Gold/Platinum)
    - _Requirements: 4.5, 3.5.1_
  
  - [ ] 22.2 Implement points and rewards system
    - Create points configuration (proper_segregation: 10pts, bulk_waste_report: 5pts, etc.)
    - Implement get_leaderboard() for ward-wise rankings
    - Create redeem_points() for reward redemption
    - _Requirements: 4.5, 3.5.1_
  
  - [ ]* 22.3 Write property test for points consistency
    - **Property 9.4.2: Total points redeemed shall never exceed total points earned**
    - **Validates: Requirements 9.4.2**
  
  - [ ]* 22.4 Write unit tests for incentive tracker
    - Test action recording
    - Test segregation verification
    - Test tier calculation
    - Test points redemption
    - _Requirements: 3.5.1, 5.6_

- [ ] 23. Implement incentive tracker API
  - [ ] 23.1 Create IncentiveAPI endpoints
    - Implement POST /citizens/register for citizen registration
    - Implement POST /actions/record for logging actions
    - Implement GET /citizens/{id}/points for points balance
    - Implement GET /leaderboard/{ward_id} for rankings
    - Implement POST /rewards/redeem for redemption
    - _Requirements: 4.5, 3.5.1_
  
  - [ ] 23.2 Implement gamification features
    - Create achievement badges system
    - Implement milestone notifications
    - Add streak tracking for consistent participation
    - _Requirements: 4.5, 3.5.1_
  
  - [ ]* 23.3 Write integration tests for incentive API
    - Test end-to-end action recording
    - Test leaderboard generation
    - Test reward redemption flow
    - _Requirements: 3.5.1, 5.6_

- [ ] 24. Build citizen mobile app UI
  - [ ] 24.1 Create React Native app structure
    - Set up React Native project
    - Configure navigation (React Navigation)
    - Implement authentication screens
    - _Requirements: 4.5, 5.5_
  
  - [ ] 24.2 Implement points and leaderboard screens
    - Create points balance display
    - Implement leaderboard view with rankings
    - Add tier badge display
    - _Requirements: 4.5, 3.5.1_
  
  - [ ] 24.3 Implement educational content
    - Create waste segregation guide screens
    - Implement interactive quizzes
    - Add personalized tips based on user history
    - Support Hindi and English
    - _Requirements: 4.5, 3.5.2_
  
  - [ ] 24.4 Implement reward redemption flow
    - Create rewards catalog screen
    - Implement redemption confirmation
    - Add redemption history
    - _Requirements: 4.5, 3.5.1_
  
  - [ ]* 24.5 Write UI tests for mobile app
    - Test screen navigation
    - Test user interactions
    - Test data display
    - _Requirements: 3.5.1, 5.6_

- [ ] 25. Checkpoint - Verify incentive tracker is functional
  - Test citizen registration and action recording
  - Verify segregation verification using CV module
  - Verify leaderboard updates correctly
  - Ensure all tests pass, ask the user if questions arise

### Phase 7: Integration and Deployment

- [ ] 26. Integrate all modules
  - [ ] 26.1 Connect CV module with forecasting
    - Pass real-time classification data to forecasting service
    - Update forecasts based on actual waste volumes
    - _Requirements: 4.1, 4.2_
  
  - [ ] 26.2 Connect forecasting with route optimization
    - Use waste predictions to optimize collection schedules
    - Adjust routes based on predicted fill levels
    - _Requirements: 4.2, 4.3_
  
  - [ ] 26.3 Connect all modules with LLM dashboard
    - Integrate CV, forecasting, and route data into dashboard
    - Enable LLM to query all data sources
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [ ] 26.4 Connect incentive tracker with CV module
    - Use CV for automated segregation verification
    - Award points based on CV classification results
    - _Requirements: 4.1, 4.5_
  
  - [ ]* 26.5 Write end-to-end integration tests
    - Test complete data flow from IoT cameras to dashboard
    - Test cross-module interactions
    - _Requirements: 5.6_

- [ ] 27. Set up monitoring and logging
  - [ ] 27.1 Implement application monitoring
    - Set up Prometheus for metrics collection
    - Configure Grafana dashboards for system health
    - Monitor API response times, error rates, throughput
    - _Requirements: 5.1, 5.3_
  
  - [ ] 27.2 Implement ML model monitoring
    - Track model inference latency
    - Monitor model accuracy drift
    - Set up alerts for model performance degradation
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [ ] 27.3 Set up centralized logging
    - Configure structured logging (JSON format)
    - Set up log aggregation (ELK stack or similar)
    - Implement log retention policies
    - _Requirements: 5.4, 5.6_

- [ ] 28. Prepare deployment infrastructure
  - [ ] 28.1 Create Docker containers for all services
    - Dockerize FastAPI backend services
    - Dockerize ML inference services
    - Dockerize LLM serving (Ollama/vLLM)
    - Create docker-compose for local development
    - _Requirements: 5.6, 6.1_
  
  - [ ] 28.2 Set up Kubernetes deployment
    - Create Kubernetes manifests for all services
    - Configure service discovery and load balancing
    - Set up persistent volumes for databases
    - Configure secrets management
    - _Requirements: 5.2, 5.3_
  
  - [ ] 28.3 Configure CI/CD pipeline
    - Set up GitHub Actions or GitLab CI
    - Implement automated testing in pipeline
    - Configure automated deployment to staging
    - _Requirements: 5.6_

- [ ] 29. Security hardening
  - [ ] 29.1 Implement API security
    - Add rate limiting to all endpoints
    - Implement request validation and sanitization
    - Configure HTTPS/TLS for all communications
    - _Requirements: 5.4_
  
  - [ ] 29.2 Secure database and data storage
    - Enable database encryption at rest
    - Configure encrypted backups
    - Implement database access controls
    - _Requirements: 5.4_
  
  - [ ] 29.3 Conduct security audit
    - Run vulnerability scanning (OWASP ZAP, Snyk)
    - Review authentication and authorization
    - Test for common vulnerabilities (SQL injection, XSS, CSRF)
    - _Requirements: 5.4_

- [ ] 30. Performance optimization
  - [ ] 30.1 Optimize database queries
    - Add indexes for frequently queried fields
    - Optimize slow queries identified in monitoring
    - Implement query result caching
    - _Requirements: 5.1_
  
  - [ ] 30.2 Optimize ML inference
    - Implement model quantization for faster inference
    - Set up batch inference where applicable
    - Configure GPU memory optimization
    - _Requirements: 5.1_
  
  - [ ] 30.3 Optimize API performance
    - Implement response compression
    - Configure CDN for static assets
    - Optimize payload sizes
    - _Requirements: 5.1_

- [ ] 31. Documentation and training
  - [ ] 31.1 Create technical documentation
    - Document API endpoints (OpenAPI/Swagger)
    - Create architecture diagrams
    - Document deployment procedures
    - _Requirements: 5.6_
  
  - [ ] 31.2 Create user documentation
    - Write admin dashboard user guide
    - Create citizen app user guide
    - Document troubleshooting procedures
    - _Requirements: 5.5_
  
  - [ ] 31.3 Prepare training materials
    - Create training videos for MCD staff
    - Prepare presentation slides for hackathon
    - Document system capabilities and limitations
    - _Requirements: 5.5_

- [ ] 32. Final testing and deployment
  - [ ] 32.1 Conduct system testing
    - Run full system test with all modules
    - Test with realistic data volumes
    - Verify all acceptance criteria are met
    - _Requirements: 5.6_
  
  - [ ] 32.2 Conduct user acceptance testing (UAT)
    - Test with MCD administrators
    - Test with sample citizens
    - Collect feedback and make adjustments
    - _Requirements: 5.5_
  
  - [ ] 32.3 Deploy to production
    - Deploy to MCD on-premise infrastructure
    - Configure production monitoring and alerts
    - Verify all services are running
    - Conduct smoke tests
    - _Requirements: 5.3_

- [ ] 33. Final checkpoint - System ready for hackathon presentation
  - All modules integrated and functional
  - System deployed and accessible
  - Presentation materials prepared
  - Demo scenarios tested and working

## Notes

- Tasks marked with `*` are optional but recommended for production quality
- Property-based tests validate correctness properties from requirements section 9
- Each checkpoint ensures phase completion before moving forward
- All LLM inference happens on-premise with no external API calls
- System designed for air-gapped deployment in government environment
