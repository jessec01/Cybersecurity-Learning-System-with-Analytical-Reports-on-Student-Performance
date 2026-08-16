import { FormField } from '../entities/FormField.js';

const usernameRegex = /^[a-zA-Z0-9_]{3,16}$/;
const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

const validateUsername = (value) => {
    if (!value || value.trim() === '') return 'El nombre de usuario es requerido';
    if (!usernameRegex.test(value)) return 'Usuario: 3-16 caracteres, solo letras, números y guión bajo';
    return null;
};

const validatePassword = (value) => {
    if (!value || value.trim() === '') return 'La contraseña es requerida';
    if (!passwordRegex.test(value)) return 'Contraseña: mínimo 8 caracteres, 1 mayúscula, 1 minúscula, 1 número y 1 carácter especial';
    return null;
};

export class LoginCredentials {
    constructor(username = '', password = '') {
        this.username = new FormField('username', username, [validateUsername]);
        this.password = new FormField('password', password, [validatePassword]);
    }

    validate() {
        const usernameValid = this.username.validate();
        const passwordValid = this.password.validate();
        return usernameValid && passwordValid;
    }

    get isValid() {
        return this.username.isValid && this.password.isValid;
    }

    get errors() {
        const errors = {};
        if (this.username.hasError) errors.username = this.username.firstError;
        if (this.password.hasError) errors.password = this.password.firstError;
        return errors;
    }

    toDTO() {
        return {
            username: this.username.value,
            password: this.password.value
        };
    }
}
