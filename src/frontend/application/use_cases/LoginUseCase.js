import { LoginFormData } from '../dto/LoginFormData.js';

export class LoginUseCase {
    constructor(apiClient, tokenStorage) {
        this.apiClient = apiClient;
        this.tokenStorage = tokenStorage;
    }

    async execute(credentials) {
        if (!credentials.validate()) {
            throw new Error('Datos de entrada inválidos');
        }

        const formData = LoginFormData.fromCredentials(credentials);
        const response = await this.apiClient.post('/auth/login', formData.toJSON());

        this.tokenStorage.save(response.access_token);

        return {
            success: true,
            token: response.access_token,
            tokenType: response.token_type
        };
    }
}
