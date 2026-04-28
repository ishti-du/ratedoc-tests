# API Testing with Newman

This directory contains Postman collections and global variables used for API testing. You can run these tests using **Newman**, the CLI tool for Postman collections.

# Prerequisites

Make sure you have the following installed:

- Node.js (which includes npm)
- Newman CLI installed globally: 
 [How to Install Newman](https://learning.postman.com/docs/collections/using-newman-cli/command-line-integration-with-newman)

```bash
npm install -g newman
```

# How to Run

1. Clone the repository

```bash
git clone https://github.com/ishti-du/ratedoc-tests.git
```

2. Go into the API directory

```bash
cd api
```

3. Run the Newman collection with globals

```bash
newman run RateDoctor.postman_collection.json -g RateDoctor.postman_globals.json
```

