#!/bin/bash

# Step 1: Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Step 2: Start PostgreSQL Service
sudo service postgresql start

# Step 3: Access PostgreSQL Shell and create database and user
sudo -u postgres psql << EOF
CREATE DATABASE warehouse;
CREATE USER warehouse_user WITH PASSWORD 'test';
GRANT ALL PRIVILEGES ON DATABASE warehouse TO warehouse_user;
EOF