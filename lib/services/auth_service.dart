import 'dart:convert';
import 'package:http/http.dart' as http;

class AuthService {
  static const String baseUrl = 'http://192.168.100.133:5000';

  Future<String> login(String usuario, String password) async {
    final url = Uri.parse('$baseUrl/api/auth/login');

    late http.Response response;

    try {
      response = await http
          .post(
            url,
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            },
            body: jsonEncode({
              'usuario': usuario,
              'password': password,
            }),
          )
          .timeout(const Duration(seconds: 15));
    } on http.ClientException {
      throw Exception(
        'No se pudo conectar con la API. Verifica la IP y que el backend esté activo.',
      );
    }

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);

      if (data is Map<String, dynamic>) {
        if (data['accessToken'] != null) {
          return data['accessToken'].toString();
        }

        if (data['access_token'] != null) {
          return data['access_token'].toString();
        }

        if (data['token'] != null) {
          return data['token'].toString();
        }
      }

      throw Exception(
        'La API respondió correctamente, pero no se encontró el token.',
      );
    }

    if (response.statusCode == 401 || response.statusCode == 403) {
      throw Exception('Usuario o contraseña incorrectos.');
    }

    throw Exception('Error de autenticación. Código HTTP: ${response.statusCode}');
  }
}