# Restaurant Marketplace

## Overview
The Restaurant Marketplace is a **scalable microservices-based platform** that allows restaurants to manage their menus, take orders, and engage customers with notifications. The system is built using **Django, gRPC, Kafka, and FastAPI**, with an API Gateway handling external interactions.

## Architecture
The platform follows a **microservices architecture**, with the following key components:

### **Core Services**
- **User Service**: Manages authentication and user data.
- **Menu Service**: Handles restaurant menus and item availability.
- **Product Service**: Stores product details and pricing.
- **Cart Service**: Manages users' cart data before checkout.
- **Order Service**: Processes and tracks orders, ensuring proper state management.
- **Notification Service**: Sends OTPs, order updates, and marketing messages via an external API.

### **Communication**
- **gRPC**: Used for internal service-to-service communication.
- **Kafka**: Used for event-driven messaging, such as sending notifications or processing order updates.
- **REST API**: External-facing API, exposed via an API Gateway.

### **Deployment**
- **Docker & Kubernetes**: The entire system is containerized for scalability.
- **CI/CD Pipelines**: Automated deployment and testing are integrated.

## Features
✅ **Multi-Restaurant Support** – Each restaurant can have multiple stores.
✅ **Recommendation System** – Uses past orders to suggest items.
✅ **Notification Handling** – Prioritized message queue for different notification types.
✅ **gRPC-based Microservices** – Efficient internal communication.
✅ **Event-driven Architecture** – Kafka ensures real-time data processing.
✅ **Scalability & Monitoring** – Designed to scale with monitoring solutions in place.

## Getting Started

### **Prerequisites**
- Docker & Docker Compose
- Kubernetes (Optional for deployment)

### **Setup Instructions**
1. Clone the repository:
   ```bash
   git clone https://github.com/rahul-jha-2001/Rasoi.git
   cd rasoi
   ```
2. Start services using Docker Compose:
   ```bash
   docker-compose up --build
   ```

## Contributing
1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-branch
   ```
3. Commit changes and push:
   ```bash
   git commit -m "Add new feature"
   git push origin feature-branch
   ```
4. Submit a pull request for review.

## Roadmap
- [ ] Implement AI-based menu item recommendations.
- [ ] Improve real-time order tracking.
- [ ] Add support for payment integrations.
- [ ] Expand multi-language support.

## License
This project is licensed under the **MIT License**. See the `LICENSE` file for details.

---
🙌 **Need Help?**
For any issues, please create a GitHub issue or reach out to the maintainers!



![image](https://github.com/user-attachments/assets/e37fad03-0ea8-4d8c-8e32-9986059490bc)
