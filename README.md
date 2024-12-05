# Site Link:

Visit the live application at: [FindMyProperty](https://findmyproperty.onrender.com)


# Equipment Management System

A Flask-based web application for managing and tracking organizational equipment, user assignments, and projects.

## Features

- **User Authentication**
  - Registration with unique employee IDs
  - Secure login/logout functionality
  - Profile management

- **Equipment Management**
  - Add, edit, and track equipment
  - Claim and release equipment
  - Equipment history tracking
  - Search functionality
  - Support for multiple equipment types

- **Project Management**
  - Create and manage projects
  - Assign team members
  - Track project status and dates

## Equipment Types Supported

- Laptop
- Desktop Computer
- Monitor
- Tablet
- Smartphone
- Printer
- Scanner
- Server
- Network Equipment
- Camera
- Projector
- Television
- Audio Equipment
- Office Furniture
- Tools
- Laboratory Equipment
- Safety Equipment
- Vehicle
- Software License
- Other

## Setup

1. Clone the repository
2. Install dependencies:


## Database Models

- **User**: Stores user information and authentication details
- **Equipment**: Tracks equipment details and assignments
- **PropertyHistory**: Maintains history of equipment assignments
- **Project**: Manages project information and team assignments

## Routes

- `/login` - User authentication
- `/register` - New user registration
- `/equipment` - View assigned equipment
- `/unclaimed_property` - View available equipment
- `/equipment/add` - Add new equipment
- `/profile` - User profile management
- `/projects` - Project management
- `/property_history/<id>` - View equipment history

## Security Features

- Password hashing
- Login required protection
- User-specific equipment access
- Manager-only project deletion
- Administrative controls for property deletion


