# NoteTakingApp

A note-taking application built with FastAPI using PostgreSQL, Redis for caching, and a Telegram Bot using Aiogram for the user interface. This app allows users to easily create, edit, and delete notes through Telegram.

## Requirements

- Python 3.12+
- Docker
- Docker Compose

## Project Structure


notions_app/
├── bot/                   # Code for Telegram Bot with Aiogram
├── api/                   # Code for FastAPI backend
├── docker-compose.yml     # Docker Compose configuration
├── requirements.txt       # Python dependencies
└── README.md              # This file

## Installation

1. Clone the repository:

   
bash
   git clone <your_repository>
   cd notions_app
   

2. Ensure that Docker and Docker Compose are installed on your machine.

3. Configure environment variables if necessary in project initialization files.

## Running the Project

To start the application, use the following command:

bash
docker-compose up --build

This command will:

- Build the images for your backend and bot.
- Start the PostgreSQL, Redis services, and your application.

Once the build is complete, you can access FastAPI at:

http://api:8000

You can also interact with your application using the Telegram Bot.

## Usage

### Interacting with the Telegram Bot

1. Find your bot in Telegram (use @BotFather to create a new bot).
2. Send commands to create, edit, and delete notes.

### API Request Examples

You can also interact with your API directly using tools like Postman or curl:

## Stopping Services

To stop all containers, you can use:

bash
docker-compose down

## Contribution

If you'd like to contribute to the project, please create a pull request with a description of your changes.


### Explanation of the README.md

- Title and Description: Starts with a brief overview of the project.
- Requirements: Lists the dependencies needed for the project.
- Project Structure: Shows how the code is organized.
- Installation and Running: Provides step-by-step instructions for setting up and running the application.
- Usage: Contains details on how to interact with the Telegram bot and provides examples of API requests.
- Stopping Services and License: Instructions on how to stop the services and information about the licensing of the project.
- Contribution: Invites others to contribute to the project.
