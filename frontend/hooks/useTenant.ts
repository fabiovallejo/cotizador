import { useAuth } from './useAuth';

export const useTenant = () => {
    const { user } = useAuth();
    return {
        empresa_id: user?.empresa_id,
        usuario_id: user?.usuario_id,
        rol: user?.rol,
    };
};