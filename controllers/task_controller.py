"""
Controlador de Tareas - Maneja la lógica de negocio de las tareas

Este archivo contiene todas las rutas y lógica relacionada con las tareas.
Representa la capa "Controlador" en la arquitectura MVC.
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from models.task import Task
from app import db


def register_routes(app):
    """
    Registra todas las rutas del controlador de tareas en la aplicación Flask
    
    Args:
        app (Flask): Instancia de la aplicación Flask
    """
    
    @app.route('/')
    def index():
        """
        Ruta principal - Redirige a la lista de tareas
        
        Returns:
            Response: Redirección a la lista de tareas
        """
        return redirect(url_for('task_list'))
    
    
    @app.route('/tasks')
    def task_list():
        """
        Muestra la lista de todas las tareas

        Query Parameters:
            filter (str): Filtro para mostrar tareas ('all', 'pending', 'completed')
            sort (str): Ordenamiento ('date', 'title', 'created')

        Returns:
            str: HTML renderizado con la lista de tareas
        """
        filter_type = request.args.get('filter', 'all')
        sort_by = request.args.get('sort', 'created')

        if filter_type not in ['all', 'pending', 'completed', 'overdue']:
            filter_type = 'all'

        if sort_by not in ['created', 'date', 'title']:
            sort_by = 'created'

        query = Task.query

        if filter_type == 'pending':
            query = query.filter_by(completed=False)
        elif filter_type == 'completed':
            query = query.filter_by(completed=True)
        elif filter_type == 'overdue':
            query = query.filter(
                Task.completed == False,
                Task.due_date.isnot(None),
                Task.due_date < datetime.utcnow()
            )

        if sort_by == 'title':
            query = query.order_by(Task.title.asc())
        elif sort_by == 'date':
            query = query.order_by(Task.due_date.asc())
        else:
            query = query.order_by(Task.created_at.desc())

        tasks = query.all()

        total_tasks = Task.query.count()
        pending_count = Task.query.filter_by(completed=False).count()
        completed_count = Task.query.filter_by(completed=True).count()

        # Datos para pasar a la plantilla
        context = {
            'tasks': tasks,
            'filter_type': filter_type,
            'sort_by': sort_by,
            'total_tasks': total_tasks,
            'pending_count': pending_count,
            'completed_count': completed_count
        }

        return render_template('task_list.html', **context)
 
    
    @app.route('/tasks/new', methods=['GET', 'POST'])
    def task_create():
        """
        Crea una nueva tarea
        
        GET: Muestra el formulario de creación
        POST: Procesa los datos del formulario y crea la tarea
        
        Returns:
            str: HTML del formulario o redirección tras crear la tarea
        """
        if request.method == 'POST':
        # implementacion de una solicitud POST
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            due_date_raw = request.form.get('due_date', '').strip()
            completed = request.form.get('completed') == 'on'

            if not title:
                flash('El título es obligatorio.', 'error')
                return render_template('task_form.html', task=None)

            due_date = None
            if due_date_raw:
                try:
                    due_date = datetime.strptime(due_date_raw, '%Y-%m-%dT%H:%M')
                except ValueError:
                    flash('La fecha de vencimiento no tiene un formato válido.', 'error')
                    return render_template('task_form.html', task=None)

            task = Task(
                title=title,
                description=description if description else None,
                due_date=due_date
            )
            task.completed = completed
            task.save()

            flash('Tarea creada correctamente.', 'success')
            return redirect(url_for('task_list'))
        
        # Mostrar formulario de creación
        return render_template('task_form.html', task=None)
    
    
    @app.route('/tasks/<int:task_id>')
    def task_detail(task_id):
        """
        Muestra los detalles de una tarea específica
        
        Args:
            task_id (int): ID de la tarea a mostrar
        
        Returns:
            str: HTML con los detalles de la tarea
        """
        pass # TODO: implementar el método
    
    
    @app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
    def task_edit(task_id):
        """
        Edita una tarea existente
        
        Args:
            task_id (int): ID de la tarea a editar
        
        GET: Muestra el formulario de edición con datos actuales
        POST: Procesa los cambios y actualiza la tarea
        
        Returns:
            str: HTML del formulario o redirección tras editar
        """
        if request.method == 'POST':
            pass # TODO: implementar para una solicitud POST
        
        # Mostrar el formulario para editar la tarea
        pass # TODO: implementar para una solicitud GET
    
    
    @app.route('/tasks/<int:task_id>/delete', methods=['POST'])
    def task_delete(task_id):
        """
        Elimina una tarea
        
        Args:
            task_id (int): ID de la tarea a eliminar
        
        Returns:
            Response: Redirección a la lista de tareas
        """
        pass # TODO: implementar el método
    
    
    @app.route('/tasks/<int:task_id>/toggle', methods=['POST'])
    def task_toggle(task_id):
        """
        Cambia el estado de completado de una tarea
        
        Args:
            task_id (int): ID de la tarea a cambiar
        
        Returns:
            Response: Redirección a la lista de tareas
        """
        pass # TODO: implementar el método
    
    
    # Rutas adicionales para versiones futuras
    
    @app.route('/api/tasks', methods=['GET'])
    def api_tasks():
        """
        API endpoint para obtener tareas en formato JSON
        (Para versiones futuras con JavaScript)
        
        Returns:
            json: Lista de tareas en formato JSON
        """
        # TODO: para versiones futuras
        return jsonify({
            'tasks': [],
            'message': 'API en desarrollo - Implementar en versiones futuras'
        })
    
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Maneja errores 404 - Página no encontrada"""
        return render_template('404.html'), 404
    
    
    @app.errorhandler(500)
    def internal_error(error):
        """Maneja errores 500 - Error interno del servidor"""
        db.session.rollback()
        return render_template('500.html'), 500

