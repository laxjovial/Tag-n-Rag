# Admin Guide: Advanced RAG System

## 1. Introduction

This guide is for system administrators. It covers all the features available in the admin dashboard, which allow you to monitor users, system configurations, and activity across the platform.

---

## 2. Accessing the Admin Dashboard

To access the admin dashboard, you must be logged in with an account that has the "admin" role.

1.  Log in to the application with your admin credentials.
2.  In the main navigation sidebar, you will see an "Admin" section with a link to the "Admin Dashboard". Click on it to open the dashboard. If you do not see this link, your account does not have admin privileges.

---

## 3. Admin Dashboard Tabs

The admin dashboard is organized into four tabs, each providing a different view of the system.

### 3.1. User Management

This tab provides a read-only view of all users registered in the system. You can see a list of all users, their assigned roles (`user` or `admin`), and their current storage usage. This usage includes both files they've uploaded directly and files they have ingested from Google Drive. This is useful for monitoring who has access to the system and how much storage each user is consuming.

*(Note: User creation, deletion, and role modification must currently be handled directly in the database.)*

### 3.2. LLM/API Configs

This tab provides a read-only view of all the LLM and external API configurations stored in the database. This allows you to verify which models and endpoints are available to the system.

*(Note: Configuration management must currently be handled directly in the database.)*

### 3.3. Global Query History

This tab provides a comprehensive, read-only log of all queries made by all users across the system. This is useful for monitoring usage, understanding user behavior, and troubleshooting issues. The table shows the query, the user who asked it, and the timestamp.

### 3.4. System Analytics

This tab provides a high-level overview of system-wide usage. The primary feature is a bar chart showing the total number of queries performed across the entire system each day. This is useful for monitoring the system's overall activity and user engagement over time.
