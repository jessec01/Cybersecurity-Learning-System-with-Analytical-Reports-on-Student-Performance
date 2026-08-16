import { LoginCredentials } from '../../domain/value_objects/LoginCredentials.js';
import { LoginUseCase } from '../../application/use_cases/LoginUseCase.js';

export class LoginForm {
    constructor(apiClient, tokenStorage) {
        this.credentials = new LoginCredentials();
        this.loginUseCase = new LoginUseCase(apiClient, tokenStorage);
        this.onSubmit = null;
        this.onError = null;
    }

    render(container) {
        container.innerHTML = `
            <form id="login-form" class="auth-form">
                <h2>Iniciar Sesión</h2>
                <div class="form-group">
                    <label for="username">Usuario</label>
                    <input type="text" id="username" name="username" placeholder="Ingrese su usuario">
                    <span class="error-message" id="username-error"></span>
                </div>
                <div class="form-group">
                    <label for="password">Contraseña</label>
                    <input type="password" id="password" name="password" placeholder="Ingrese su contraseña">
                    <span class="error-message" id="password-error"></span>
                </div>
                <div id="general-error" class="error-message"></div>
                <button type="submit" class="btn-primary">Iniciar Sesión</button>
                <p class="form-footer">
                    ¿No tiene cuenta? <a href="admin-register.html">Registrar admin</a>
                </p>
            </form>
        `;

        this.setupEventListeners(container);
    }

    setupEventListeners(container) {
        const form = container.querySelector('#login-form');
        const usernameInput = container.querySelector('#username');
        const passwordInput = container.querySelector('#password');

        usernameInput.addEventListener('input', (e) => {
            this.credentials.username.setValue(e.target.value);
            this.credentials.username.touch();
            this.showFieldError('username', this.credentials.username.firstError);
        });

        passwordInput.addEventListener('input', (e) => {
            this.credentials.password.setValue(e.target.value);
            this.credentials.password.touch();
            this.showFieldError('password', this.credentials.password.firstError);
        });

        usernameInput.addEventListener('blur', () => {
            this.credentials.username.touch();
            this.showFieldError('username', this.credentials.username.firstError);
        });

        passwordInput.addEventListener('blur', () => {
            this.credentials.password.touch();
            this.showFieldError('password', this.credentials.password.firstError);
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleSubmit();
        });
    }

    showFieldError(fieldName, message) {
        const errorElement = document.getElementById(`${fieldName}-error`);
        const inputElement = document.getElementById(fieldName);

        if (errorElement) {
            errorElement.textContent = message || '';
        }

        if (inputElement) {
            if (message) {
                inputElement.classList.add('input-error');
            } else {
                inputElement.classList.remove('input-error');
            }
        }
    }

    showGeneralError(message) {
        const errorElement = document.getElementById('general-error');
        if (errorElement) {
            errorElement.textContent = message || '';
        }
    }

    async handleSubmit() {
        this.showGeneralError('');

        this.credentials.username.touch();
        this.credentials.password.touch();

        if (!this.credentials.validate()) {
            this.showFieldError('username', this.credentials.username.firstError);
            this.showFieldError('password', this.credentials.password.firstError);
            return;
        }

        try {
            const result = await this.loginUseCase.execute(this.credentials);

            if (this.onSubmit) {
                this.onSubmit(result);
            }
        } catch (error) {
            this.showGeneralError(error.message || 'Error al iniciar sesión');

            if (this.onError) {
                this.onError(error);
            }
        }
    }
}
