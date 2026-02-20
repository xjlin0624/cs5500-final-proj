# CS5500 Final Project: AfterCart

*group 1: Yingchao Cai, Bo Hu, Xuelan Lin, Weiyi Sun*

This project builds a “Post-Purchase Uncertainty Reducer” that helps shoppers feel confident after checkout by aggregating orders across retailers, monitoring price/delivery/recurring-spend risks, and providing clear, actionable recommendations (price match, return/rebuy, replacement, or no action).


## Objectives 

### MVP

1. Cross-retailer Order Aggregation
2. Price Drop and Better-Deal Monitoring
3. Delivery Anomaly Detection and Plan B Recommendations
4. Unused Subscription and Recurring-Spend Detection
5. Decision-Confidence Visualization
6. Customer Support Message Assistance

### Stretch Goals
7. Personalized Recommendation Tuning
8. Amazon Retailer Integration

## Functional Requirements

### Authentication & User Settings

- **FR-1 (MUST)** User Authentication

- **FR-2 (MUST)** User Preferences

### Order Capture & Aggregation

- **FR-3 (MUST)** Order Capture via Extension

- **FR-4 (MUST)** Order De-duplication

- **FR-5 (MUST)** Centralized Order View

### Price Monitoring & Price History

- **FR-6 (MUST)** Price History Storage

- **FR-7 (MUST)** Price Drop Detection

- ***FR-8 (SHOULD)** Same-Retailer Alternative Product Detection*

### Recommendation Engine

- **FR-9 (MUST)** Action Recommendation

- **FR-10 (MUST)** Explainable Recommendation Output

### Alerts & Notifications

- **FR-11 (MUST)** Alert Management

- **FR-12 (MUST)** Notification Delivery

### Delivery Monitoring

- **FR-13 (MUST)** Delivery ETA Monitoring

- ***FR-14 (SHOULD)** Plan-B Suggestions for Delays*

### Subscription & Recurring Spend Detection

- **FR-15 (MUST)** Recurring Purchase/Subscription Flags

- **FR-16 (MUST)** Cancellation Guidance

### Customer Support Message Assistance & Evidence

- **FR-17 (MUST)** Message Templates

- **FR-18 (MUST)** Evidence Bundling

### Outcome Tracking & Savings

- **FR-19 (MUST)** User Outcome Logging

- **FR-20 (MUST)** Savings Dashboard