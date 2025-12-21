// @ts-nocheck
import { onMount } from 'solid-js';
import { useNavigate, useParams } from '@solidjs/router';

// Legacy Portuguese project detail route: redirect to English /projects/:id
export default function LegacyProjectDetailRedirect() {
  const params = useParams();
  const navigate = useNavigate();
  onMount(() => navigate(`/projects/${params.id}`, { replace: true }));
  return null;
}
