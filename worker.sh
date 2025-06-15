#!/bin/bash

export $(grep -v '^#' .env | xagrs -d '\n')
rq worker --with-scheduler --url redis://valkey:6379