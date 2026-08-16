import { AdminRegistrationData } from '../../domain/value_objects/AdminRegistrationData.js';
import { AdminRegistrationUseCase } from '../../application/use_cases/AdminRegistrationUseCase.js';

export class AdminRegistrationForm {
    constructor(apiClient) {
        this.registrationData = new AdminRegistrationData();
        this.registrationUseCase = new AdminRegistrationUseCase(apiClient);
        this.onSubmit = null;
        this.onError = null;
    }

    render(container) {
        container.innerHTML = `
            <form id="admin-register-form" class="auth-form">
                <h2>Registrar Administrador</h2>
                <div class="form-section">
                    <h3>Datos de Usuario</h3>
                    <div class="form-group">
                        <label for="username">Usuario</label>
                        <input type="text" id="username" name="username" placeholder="Ingrese el usuario">
                        <span class="error-message" id="username-error"></span>
                    </div>
                    <div class="form-group">
                        <label for="password">Contraseña</label>
                        <input type="password" id="password" name="password" placeholder="Ingrese la contraseña">
                        <span class="error-message" id="password-error"></span>
                    </div>
                </div>
                <div class="form-section">
                    <h3>Datos Personales</h3>
                    <div class="form-group">
                        <label for="firstName">Nombre</label>
                        <input type="text" id="firstName" name="firstName" placeholder="Ingrese el nombre">
                        <span class="error-message" id="firstName-error"></span>
                    </div>
                    <div class="form-group">
                        <label for="lastName">Apellido</label>
                        <input type="text" id="lastName" name="lastName" placeholder="Ingrese el apellido">
                        <span class="error-message" id="lastName-error"></span>
                    </div>
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" id="email" name="email" placeholder="Ingrese el email">
                        <span class="error-message" id="email-error"></span>
                    </div>
                    <div class="form-group">
                        <label for="phone">Teléfono (opcional)</label>
                        <input type="tel" id="phone" name="phone" placeholder="Ingrese el teléfono">
                        <span class="error-message" id="phone-error"></span>
                    </div>
                </div>
                <div id="general-error" class="error-message"></div>
                <button type="submit" class="btn-primary">Registrar Administrador</button>
                <p class="form-footer">
                    ¿Ya tiene cuenta? <a href="/">Iniciar sesión</a>
                </p>
            </form>
        `;

        this.setupEventListeners(container);
    }

    setupEventListeners(container) {
        const form = container.querySelector('#admin-register-form');
        const fields = ['username', 'password', 'firstName', 'lastName', 'email', 'phone'];

        fields.forEach(fieldName => {
            const input = container.querySelector(`#${fieldName}`);
            const valueObject = this.getField(fieldName);

            if (input && valueObject) {
                input.addEventListener('input', (e) => {
                    valueObject.setValue(e.target.value);
                    valueObject.touch();
                    this.showFieldError(fieldName, valueObject.firstError);
                });

                input.addEventListener('blur', () => {
                    valueObject.touch();
                    this.showFieldError(fieldName, valueObject.firstError);
                });
            }
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleSubmit();
        });
    }

    getField(fieldName) {
        const fieldMap = {
            username: this.registrationData.username,
            password: this.registrationData.password,
            firstName: this.registrationData.firstName,
            lastName: this.registrationData.lastName,
            email: this.registrationData.email,
            phone: this.registrationData.phone
        };
        return fieldMap[fieldName];
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

        const fields = ['username', 'password', 'firstName', 'lastName', 'email', 'phone'];
        fields.forEach(fieldName => {
            this.getField(fieldName).touch();
        });

        if (!this.registrationData.validate()) {
            fields.forEach(fieldName => {
                const field = this.getField(fieldName);
                this.showFieldError(fieldName, field.firstError);
            });
            return;
        }

        try {
            const result = await this.registrationUseCase.execute(this.registrationData);

            if (this.onSubmit) {
                this.onSubmit(result);
            }
        } catch (error) {
            this.showGeneralError(error.message || 'Error al registrar administrador');

            if (this.onError) {
                this.onError(error);
            }
        }
    }
}
