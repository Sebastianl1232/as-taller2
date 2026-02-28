"""
Controlador de autenticación - Registro e inicio/cierre de sesión
"""

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from models.user import User
from app import db


def register_auth_routes(app):
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('task_list'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')

            if not username or not email or not password:
                flash('Todos los campos obligatorios deben completarse.', 'error')
                return render_template('register.html')

            if password != confirm_password:
                flash('Las contraseñas no coinciden.', 'error')
                return render_template('register.html')

            if len(password) < 6:
                flash('La contraseña debe tener al menos 6 caracteres.', 'error')
                return render_template('register.html')

            if User.query.filter_by(username=username).first():
                flash('Ese nombre de usuario ya está en uso.', 'error')
                return render_template('register.html')

            if User.query.filter_by(email=email).first():
                flash('Ese correo ya está registrado.', 'error')
                return render_template('register.html')

            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            login_user(user)
            flash('Registro exitoso. ¡Bienvenido!', 'success')
            return redirect(url_for('task_list'))

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('task_list'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')

            user = User.query.filter_by(username=username).first()
            if user is None or not user.check_password(password):
                flash('Usuario o contraseña inválidos.', 'error')
                return render_template('login.html')

            login_user(user)
            next_url = request.args.get('next')
            flash('Sesión iniciada correctamente.', 'success')
            return redirect(next_url or url_for('task_list'))

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        logout_user()
        flash('Has cerrado sesión.', 'info')
        return redirect(url_for('login'))
