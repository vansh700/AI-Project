Endpoint

POST /analysis

Purpose

Creates analysis job.

Owner

MS1

Authentication

Required

Request

{}

Response

{}

Possible Errors

400

401

404

500

Internal Flow

Frontend

↓

MS1 Controller

↓

Analysis Service

↓

BullMQ

↓

Return Job ID