import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = 'http://192.168.100.133:5000';

  Future<List<dynamic>> obtenerCamiones(String token) async {
    final url = Uri.parse('$baseUrl/api/camiones');

    try {
      final response = await http
          .get(
            url,
            headers: {
              'Accept': 'application/json',
              'Authorization': 'Bearer $token',
            },
          )
          .timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        if (data is List) {
          return data;
        }

        throw Exception('La API no devolvió una lista de camiones.');
      }

      if (response.statusCode == 401) {
        throw Exception(
          'No autorizado. El token es incorrecto o ha expirado.',
        );
      }

      if (response.statusCode == 403) {
        throw Exception(
          'Acceso denegado. El usuario no tiene permisos.',
        );
      }

      throw Exception(
        'Error al obtener camiones. Código HTTP: ${response.statusCode}',
      );
    } on http.ClientException {
      throw Exception(
        'No se pudo conectar con la API. Verifica la IP y que el backend esté activo.',
      );
    } on FormatException {
      throw Exception('La API devolvió una respuesta JSON inválida.');
    }
  }
}