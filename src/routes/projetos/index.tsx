// @ts-nocheck
import { onMount } from 'solid-js';
import { useNavigate } from '@solidjs/router';

// Legacy Portuguese route: redirect to English /projects
export default function LegacyProjectsRedirect() {
  const navigate = useNavigate();
  onMount(() => navigate('/projects', { replace: true }));
  return null;
}
