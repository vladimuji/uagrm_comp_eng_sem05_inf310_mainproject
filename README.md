# Data Structures II (INF310) - Python Implementation

A comprehensive Python implementation of fundamental data structures, developed as part of the **INF310 - Data Structures II** course at UAGRM (Universidad Autónoma Gabriel René Moreno).

## 📋 Overview

This project provides clean, educational implementations of common data structures following **PEP8** Python coding standards. It's designed as a learning resource for understanding the internal mechanics and properties of various data structures.

## 📁 GOOGLE COLAB
- **[Google Colab where you can test and run the exercices](https://colab.research.google.com/drive/1U2pN--lMrr6kjuH7DZrutDfrbOXlNpAg?usp=sharing)**

## 📁 EXERCICES - HOMEWORK

- **[UNIDAD 0 - Retos :Ejercicios propuestos Sobre estandares y buenas practicas](https://github.com/vladimuji/uagrm_comp_eng_sem05_inf310_mainproject/blob/uni_1_reto_tic_tac_toe_strategy/exercices/pep8.py)**
- **[UNIDAD 0 - Tarea sobre estandar de condificación](https://github.com/vladimuji/uagrm_comp_eng_sem05_inf310_mainproject/blob/uni_1_reto_tic_tac_toe_strategy/bin_tree/binary_tree.py)**
- **[UNIDAD 1 - Reto : Implementar el ADT Arboles Binarios (Juego Tres en raya)](https://github.com/vladimuji/uagrm_comp_eng_sem05_inf310_mainproject/blob/uni_1_reto_tic_tac_toe_strategy/exercices/tic_tac_toe_strategy.py)**
- **[UNIDAD 1 - Arbol binario: Implemetacion de metodos](https://github.com/vladimuji/uagrm_comp_eng_sem05_inf310_mainproject/blob/uni_1_bintree_meth_implem/bin_tree/binary_tree.py)**
- **[UNIDAD 1 - Tarea : Representacion del ADT Arboles binarios de busquedas](https://github.com/vladimuji/uagrm_comp_eng_sem05_inf310_mainproject/blob/unit_1_search_bintree/bin_tree/search_binary_tree.py)**
- **[UNIDAD 1 - Tarea : Implementar Árbol de Expresión para evaluar cadena infija](https://github.com/vladimuji/uagrm_comp_eng_sem05_inf310_mainproject/blob/unit_1_expression_tree/bin_tree/expression_tree.py)**
- **[UNIDAD 1 - Tarea unidad 1: Implementar metodos de Arboles Binarios AVL](https://github.com/vladimuji/uagrm_comp_eng_sem05_inf310_mainproject/blob/unit_1_avl_tree_implementation/bin_tree/avl_tree.py)**
- **[UNIDAD 1 - Tarea unidad 1: Crear interfaz grafica]()**
- **[UNIDAD 1 - Arbol binario: Metodo eliminar y AVL](https://github.com/vladimuji/uagrm_comp_eng_sem05_inf310_mainproject/blob/unit_1_avl_tree_implementation/bin_tree/avl_tree.py)**

## 📁 Project Structure

```
00-code/
    ├── config/                     # Django project configuration
    │   ├── asgi.py                 # ASGI entry point for asynchronous servers
    │   ├── settings.py             # Application, database, and template settings
    │   ├── urls.py                 # Main URL routes, including the home page
    │   └── wsgi.py                 # WSGI entry point for deployment servers
    ├── datastructures/             # Data structure implementations
    │   ├── bin_tree/               # Binary tree implementations
    │   │   ├── avl_tree.py         # Self-balancing AVL tree
    │   │   ├── binary_tree.py      # BinaryNode and BinaryTree classes
    │   │   ├── expression_tree.py  # Tree for evaluating expressions
    │   │   ├── search_binary_tree.py # Binary search tree implementation
    │   │   └── data/               # Binary tree test data
    │   ├── graph/                  # Graph data structure and datasets
    │   │   └── data/               # Graph test data
    │   └── heap/                   # Heap data structure
    ├── exercices/                 # Course exercises and practice projects
    │   ├── pep8.py                # PEP8 coding standards examples
    │   ├── tic_tac_toe.py         # Tic-Tac-Toe game
    │   └── tic_tac_toe_strategy.py # Tic-Tac-Toe strategy using a binary tree
    ├── logistics/                 # Django application for the web interface
    │   ├── migrations/            # Database migration files
    │   ├── static/logistics/
    │   ├   └── css/
    │   │       └── styles.css
    │   ├   └── js/
    │   │       └── menu.js
    │   ├   └── images/
    │   ├── services/              # MODELS (ORM)
    │   │   └── graph_service.py
    │   │   └── heap_service.py
    │   │   └── tree_service.py
    │   ├── models/                # MODELS (ORM)
    │   │   └── node.py
    │   │   └── route.py
    │   ├── views/                 # VIEWS (Controllers)
    │   │   └── views.py           # Views that render the web pages
    │   ├── templates/logistics/   # TEMPLATES (Views)
    │   │   ├── base.html          # Main project home page
    │   │   ├── graph_view.html    # Graph visualization template
    │   │   └── tree_view.html     # Tree visualization template
    │   ├── admin.py               # Django administration configuration
    │   ├── apps.py                # Application configuration
    │   └── tests.py               # Application tests
    ├── db.sqlite3                 # Local SQLite database
    ├── main.py                    # Main Python entry point
    ├── manage.py                  # Django command-line utility
    ├── README.md                  # Project documentation
    └── requirements.txt           # Python project dependencies
```

## 🌳 Binary Tree Implementation

### Features
- **BinaryNode**: Represents individual nodes with data, left child, and right child
- **BinaryTree**: Base class for binary tree structure with utility methods
- **Property-based access**: Uses Python properties for clean getter/setter patterns
- **PEP8 compliant**: Follows Python style guidelines throughout

### Classes

#### BinaryNode
```python
node = BinaryNode(data=10)
node.left_child = BinaryNode(5)
node.right_child = BinaryNode(15)
```

#### BinaryTree
```python
tree = BinaryTree()
tree.root = BinaryNode(1)
```

### Methods
- `is_empty_tree()` - Check if tree has no root
- `is_leaf(node)` - Check if node has no children
- `create_node(data)` - Factory method to create new nodes
- Property-based access to tree root

## 📊 Additional Data Structures

- **Graph**: Graph traversal and manipulation algorithms
- **Heap**: Heap data structure for priority queue operations

## 🛠️ Technologies

- **Language**: Python 3.x
- **Code Style**: PEP8 compliant
- **Features**: Object-oriented design with properties and context managers

## 📚 PEP8 Standards

The project includes examples of Python best practices:
- Proper naming conventions
- Docstring formatting
- Context managers
- Type hints in documentation
- Clean code organization

See `exercices/pep8.py` for detailed examples.

## 🚀 Getting Started

### Prerequisites
- Python 3.6+

### Usage

```python
from bin_tree.BinaryTree import BinaryTree, BinaryNode

# Create a binary tree
tree = BinaryTree()

# Create nodes
root = tree.create_node(10)
tree.root = root

# Add children
root.left_child = tree.create_node(5)
root.right_child = tree.create_node(15)

# Check tree properties
print(tree.is_empty_tree())  # False
print(tree.is_leaf(root))     # False
```

## 📖 Course Information

- **Course**: INF310 - Data Structures II
- **Institution**: UAGRM (Universidad Autónoma Gabriel René Moreno)
- **Semester**: 5th Semester
- **Author**: Vladimir

## 📝 Notes

This is an educational project focused on:
- Understanding core data structure concepts
- Writing clean, maintainable Python code
- Practicing PEP8 coding standards
- Building strong fundamentals in algorithms and data structures

## 📄 License

Educational project for academic purposes.

---

**Feel free to fork, study, and use this as a reference for your own data structures learning journey!**
