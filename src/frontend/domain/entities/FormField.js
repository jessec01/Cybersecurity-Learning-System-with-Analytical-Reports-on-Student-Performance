export class FormField {
    constructor(name, value, validators = []) {
        this.name = name;
        this.value = value;
        this.validators = validators;
        this.errors = [];
        this.touched = false;
    }

    validate() {
        this.errors = [];
        for (const validator of this.validators) {
            const error = validator(this.value);
            if (error) {
                this.errors.push(error);
            }
        }
        return this.errors.length === 0;
    }

    setValue(value) {
        this.value = value;
        if (this.touched) {
            this.validate();
        }
    }

    touch() {
        this.touched = true;
        this.validate();
    }

    get isValid() {
        return this.errors.length === 0;
    }

    get hasError() {
        return this.touched && this.errors.length > 0;
    }

    get firstError() {
        return this.errors[0] || null;
    }
}
