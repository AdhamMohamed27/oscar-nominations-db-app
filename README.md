# 🎬 Oscar Nominations Database App

A database-driven web application that allows users to explore Oscar nomination data across different iterations and categories. Users can view which individuals, movies, or entities were nominated or won in each year — and can also create their own custom Oscar-style nomination tables.

---

## 📌 Project Overview

This project serves as both a **historical archive** and an **interactive tool** for managing and analyzing Academy Award (Oscar) nominations. Built using modern database practices, the app allows users to:

- View nominees and winners for each Oscar year (iteration)
- Browse by person, movie, category, or award type
- Create and manage their own custom Oscar nomination datasets

---

## ⚙️ Features

- 🗃️ View official nominees and winners by year
- 🔍 Search by actor, director, film, or category
- 🏆 Highlight winners in each category
- ✍️ Create your own Oscar-style nominations
- 💾 Save custom nomination tables to the database

---

## 🛠️ Tech Stack

- **Backend:** PostgreSQL / MySQL
- **Frontend:** HTML/CSS, JavaScript (or React)
- **Framework:** Flask / Django / Node.js (choose based on your implementation)
- **Database Tools:** SQLAlchemy / Sequelize / Django ORM

---

## 📊 Example Schema

```sql
Tables:
- nominations (id, year, category_id, nominee_id, won)
- nominees (id, name, type [person/movie])
- categories (id, name)
- users (id, username, password)
- custom_nominations (id, user_id, category_id, nominee_id, year, won)
