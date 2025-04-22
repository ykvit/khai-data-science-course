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

### 🚩 Run Lab 4

Lab 4 Upgrading of the programme for processing and analysing student performance data with an enhanced console interface, graphical display and report generation.


**Build the Docker image:**

```bash
   cd lab4
   docker build -t lab4 .
   docker run --rm -v "$(pwd)/output:/app/output" lab4
```

**Docker compose:**

```bash
    docker-compose build lab4
    docker-compose run lab4
```

---

### 🚩 Run Lab 5

Lab 4 Development of a graphical interface for a programme for processing and analysing student performance data.


**Build the Docker image:**

```bash
   cd lab5
   docker build -t lab5 .
   docker run --rm -v "$(pwd)/output:/app/output" lab5
```

**Docker compose:**

```bash
    docker-compose build lab5
    docker-compose run lab5
```
---

### Cleanup

```bash
    docker system prune
```
