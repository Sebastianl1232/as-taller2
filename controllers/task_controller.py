"""
Controlador de Tareas - Maneja la lógica de negocio de las tareas

Este archivo contiene todas las rutas y lógica relacionada con las tareas.
Representa la capa "Controlador" en la arquitectura MVC.
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from sqlalchemy import case
from flask_login import current_user, login_required
from models.task import Task
from models.user import TaskOwner
from app import db


def register_routes(app):
    """
    Registra todas las rutas del controlador de tareas en la aplicación Flask
    
    Args:
        app (Flask): Instancia de la aplicación Flask
    """
    
    def _user_tasks_query():
        return Task.query.join(TaskOwner, TaskOwner.task_id == Task.id).filter(
            TaskOwner.user_id == current_user.id
        )

    def _get_user_task(task_id):
        return _user_tasks_query().filter(Task.id == task_id).first_or_404()

    @app.route('/')
    def index():
        """
        Ruta principal - Redirige a la lista de tareas
        
        Returns:
            Response: Redirección a la lista de tareas
        """
        return redirect(url_for('task_list'))
    
    
    @app.route('/tasks')
    @login_required
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

        query = _user_tasks_query()

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
            query = query.order_by(
                case((Task.due_date.is_(None), 1), else_=0),
                Task.due_date.asc()
            )
        else:
            query = query.order_by(Task.created_at.desc())

        tasks = query.all()

        total_tasks = _user_tasks_query().count()
        pending_count = _user_tasks_query().filter_by(completed=False).count()
        completed_count = _user_tasks_query().filter_by(completed=True).count()

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
    @login_required
    def task_create():
        """
        Crea una nueva tarea
        
        GET: Muestra el formulario de creación
        POST: Procesa los datos del formulario y crea la tarea
        
        Returns:
            str: HTML del formulario o redirección tras crear la tarea
        """
        if request.method == 'POST':
            # implementación de una solicitud POST
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            due_date_raw = request.form.get('due_date', '').strip()
            completed = request.form.get('completed') == 'on'

            if not title:
                flash('El título es obligatorio.', 'error')
                return render_template('task_form.html', task=None)
            if len(title) > 200:
                flash('El título no puede tener más de 200 caracteres.', 'error')
                return render_template('task_form.html', task=None)
            if len(description) > 1000:
                flash('La descripción no puede tener más de 1000 caracteres.', 'error')
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

            db.session.add(task)
            db.session.flush()
            db.session.add(TaskOwner(user_id=current_user.id, task_id=task.id))
            db.session.commit()

            flash('Tarea creada correctamente.', 'success')
            return redirect(url_for('task_list'))
        
        # Mostrar formulario de creación
        return render_template('task_form.html', task=None)
    
    
    @app.route('/tasks/<int:task_id>')
    @login_required
    def task_detail(task_id):
        """
        Muestra los detalles de una tarea específica
        
        Args:
            task_id (int): ID de la tarea a mostrar
        
        Returns:
            str: HTML con los detalles de la tarea
        """
        return redirect(url_for('task_edit', task_id=task_id))
    
    
    @app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
    @login_required
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
        task = _get_user_task(task_id)

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            due_date_raw = request.form.get('due_date', '').strip()
            completed = request.form.get('completed') == 'on'

            if not title:
                flash('El título es obligatorio.', 'error')
                return render_template('task_form.html', task=task)
            if len(title) > 200:
                flash('El título no puede tener más de 200 caracteres.', 'error')
                return render_template('task_form.html', task=task)
            if len(description) > 1000:
                flash('La descripción no puede tener más de 1000 caracteres.', 'error')
                return render_template('task_form.html', task=task)

            due_date = None
            if due_date_raw:
                try:
                    due_date = datetime.strptime(due_date_raw, '%Y-%m-%dT%H:%M')
                except ValueError:
                    flash('La fecha de vencimiento no tiene un formato válido.', 'error')
                    return render_template('task_form.html', task=task)

            task.title = title
            task.description = description if description else None
            task.due_date = due_date
            task.completed = completed

            db.session.commit()

            flash('Tarea actualizada correctamente.', 'success')
            return redirect(url_for('task_list'))
        
        # Mostrar el formulario para editar la tarea
        return render_template('task_form.html', task=task)
    
    
    @app.route('/tasks/<int:task_id>/delete', methods=['POST'])
    @login_required
    def task_delete(task_id):
        """
        Elimina una tarea
        
        Args:
            task_id (int): ID de la tarea a eliminar
        
        Returns:
            Response: Redirección a la lista de tareas
        """
        task = _get_user_task(task_id)
        task.delete()
        flash('Tarea eliminada correctamente.', 'success')
        return redirect(url_for('task_list'))
    
    
    @app.route('/tasks/<int:task_id>/toggle', methods=['POST'])
    @login_required
    def task_toggle(task_id):
        """
        Cambia el estado de completado de una tarea
        
        Args:
            task_id (int): ID de la tarea a cambiar
        
        Returns:
            Response: Redirección a la lista de tareas
        """
        task = _get_user_task(task_id)

        if task.completed:
            task.mark_pending()
            message = 'Tarea marcada como pendiente.'
        else:
            task.mark_completed()
            message = 'Tarea marcada como completada.'

        db.session.commit()
        flash(message, 'success')
        return redirect(url_for('task_list'))
    
    
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
        return render_template(
            'error.html',
            title='Página no encontrada',
            breadcrumb='Error 404',
            icon='search',
            color='warning',
            heading='404 - Página no encontrada',
            message='La URL solicitada no existe o fue movida.'
        ), 404
    
    
    @app.errorhandler(500)
    def internal_error(error):
        """Maneja errores 500 - Error interno del servidor"""
        db.session.rollback()
        return render_template(
            'error.html',
            title='Error interno',
            breadcrumb='Error 500',
            icon='exclamation-triangle',
            color='danger',
            heading='500 - Error interno del servidor',
            message='Ocurrió un problema inesperado. Inténtalo nuevamente.'
        ), 500

