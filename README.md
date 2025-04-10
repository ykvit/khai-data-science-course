# KHAI Data Science Labs

This repository contains a set of labs for Data Science tasks developed at KHAI. Each lab is organized in its own folder with Docker support for reproducibility and isolation.



### 🚩 Run Lab 1

Lab 1 Operations with numbers and expressions in Python.

**Build the Docker image:**

```bash
    cd lab1
    docker build -t lab1 .
    docker run --rm lab1
```

**Docker compose:**

```bash
    docker-compose build lab1
    docker-compose run lab1
```

---
### 🚩 Run Lab 2

Lab 2 Processing and analyzing data on people's physical characteristics.


**Build the Docker image:**

```bash
   cd lab2
   docker build -t lab2 .
   docker run --rm -v "$(pwd)/output:/app/output" lab2
```

**Docker compose:**

```bash
    docker-compose build lab2
    docker-compose run lab2
```

---

### 🚩 Run Lab 3

Lab 3 Processing and analyzing student performance data using Pandas.


**Build the Docker image:**

```bash
   cd lab3
   docker build -t lab3 .
   docker run --rm -v "$(pwd)/output:/app/output" lab3
```

**Docker compose:**

```bash
    docker-compose build lab3
    docker-compose run lab3
```

---

### Cleanup

```bash
    docker system prune
```
