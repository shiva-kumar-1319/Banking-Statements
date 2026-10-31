from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .assistant_service import ask_ai_assistant


class AssistantChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        query = request.data.get('message') or request.data.get('query')
        if not query or not str(query).strip():
            return Response({"error": "Please provide a query message."}, status=status.HTTP_400_BAD_REQUEST)

        result = ask_ai_assistant(request.user, str(query).strip())
        return Response(result)
