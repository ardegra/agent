# ARDegra Agent

This is a simple agent for all crawler managed by ARDegra. Here is the simplest flow

  1. API insert a new job inside `agentJobs` collection
  2. Agent will read the job and run the spider based on the job description.

## Installation
We recommend to install ARDegra Agent only using Docker
  1. `docker pull ardegra/agent`
  2. `docker run -d --name ardegra.agent ardegra/agent`