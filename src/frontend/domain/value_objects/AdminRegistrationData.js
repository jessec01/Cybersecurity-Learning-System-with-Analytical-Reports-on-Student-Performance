import { FormField } from '../entities/FormField.js';

const usernameRegex = /^[a-zA-Z0-9_]{3,16}$/;
const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const phoneRegex = /^\+?[\d\s-]{7,15}$/;

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

const validateFirstName = (value) => {
    if (!value || value.trim() === '') return 'El nombre es requerido';
    if (value.trim().length < 2) return 'El nombre debe tener al menos 2 caracteres';
    return null;
};

const validateLastName = (value) => {
    if (!value || value.trim() === '') return 'El apellido es requerido';
    if (value.trim().length < 2) return 'El apellido debe tener al menos 2 caracteres';
    return null;
};

const validateEmail = (value) => {
    if (!value || value.trim() === '') return 'El email es requerido';
    if (!emailRegex.test(value)) return 'Ingrese un email válido';
    return null;
};

const validatePhone = (value) => {
    if (!value || value.trim() === '') return null; // Phone is optional
    if (!phoneRegex.test(value)) return 'Ingrese un teléfono válido';
    return null;
};

export class AdminRegistrationData {
    constructor(data = {}) {
        this.username = new FormField('username', data.username || '', [validateUsername]);
        this.password = new FormField('password', data.password || '', [validatePassword]);
        this.firstName = new FormField('firstName', data.firstName || '', [validateFirstName]);
        this.lastName = new FormField('lastName', data.lastName || '', [validateLastName]);
        this.email = new FormField('email', data.email || '', [validateEmail]);
        this.phone = new FormField('phone', data.phone || '', [validatePhone]);
    }

    validate() {
        const fields = [this.username, this.password, this.firstName, this.lastName, this.email, this.phone];
        return fields.every(field => field.validate());
    }

    get isValid() {
        return this.username.isValid && this.password.isValid && this.firstName.isValid &&
               this.lastName.isValid && this.email.isValid && this.phone.isValid;
    }

    get errors() {
        const errors = {};
        if (this.username.hasError) errors.username = this.username.firstError;
        if (this.password.hasError) errors.password = this.password.firstError;
        if (this.firstName.hasError) errors.firstName = this.firstName.firstError;
        if (this.lastName.hasError) errors.lastName = this.lastName.firstError;
        if (this.email.hasError) errors.email = this.email.firstError;
        if (this.phone.hasError) errors.phone = this.phone.firstError;
        return errors;
    }

    toDTO() {
        return {
            username: this.username.value,
            password: this.password.value,
            first_name: this.firstName.value,
            last_name: this.lastName.value,
            mail: this.email.value,
            phone: this.phone.value || null
        };
    }
}
