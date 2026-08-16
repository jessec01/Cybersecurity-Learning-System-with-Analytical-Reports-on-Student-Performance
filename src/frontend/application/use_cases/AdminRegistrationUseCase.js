import { AdminRegistrationFormData } from '../dto/AdminRegistrationFormData.js';

export class AdminRegistrationUseCase {
    constructor(apiClient) {
        this.apiClient = apiClient;
    }

    async execute(registrationData) {
        if (!registrationData.validate()) {
            throw new Error('Datos de entrada inválidos');
        }

        const formData = AdminRegistrationFormData.fromRegistrationData(registrationData);
        const response = await this.apiClient.post('/auth/register', formData.toJSON());

        return {
            success: true,
            message: response.message
        };
    }
}
