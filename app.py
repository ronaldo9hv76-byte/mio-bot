
import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
import io

st.set_page_config(layout="wide", page_title="Face Modeller", page_icon="🎭")

# Inizializza MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True)

def apply_local_distortion(image, cx, cy, radius, strength):
    h, w = image.shape[:2]
    x, y = np.meshgrid(np.arange(w), np.arange(h))
    
    # Calcolo distanza euclidea dal centro
    dx, dy = x - cx, y - cy
    r = np.sqrt(dx**2 + dy**2)
    
    # Maschera circolare per l'area di effetto
    mask = r < radius
    
    map_x = x.astype(np.float32)
    map_y = y.astype(np.float32)
    
    if strength != 0:
        r_norm = r / radius
        r_norm[r_norm == 0] = 1 
        
        # Logica per l'effetto lente convessa (bulge) o concava (pinch)
        distortion = 1.0 + (strength * (1.0 - r_norm)**2)
        
        map_x[mask] = cx + dx[mask] / distortion[mask]
        map_y[mask] = cy + dy[mask] / distortion[mask]
    
    # Rimappatura dei pixel
    deformed = cv2.remap(image, map_x, map_y, interpolation=cv2.INTER_LINEAR)
    return deformed

st.title("🎭 Modellazione Facciale Interattiva")
st.write("Carica un'immagine per deformare dinamicamente naso, occhi e bocca.")

uploaded_file = st.file_uploader("Carica un'immagine (JPG, PNG)", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert('RGB')
    img_array = np.array(image)
    h, w = img_array.shape[:2]
    
    # Rilevamento dei punti con MediaPipe
    results = face_mesh.process(img_array)
    
    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark
        
        # Mappatura delle coordinate in base alla risoluzione
        pt_naso = (int(landmarks[1].x * w), int(landmarks[1].y * h))
        pt_occhio_sx = (int(landmarks[159].x * w), int(landmarks[159].y * h))
        pt_occhio_dx = (int(landmarks[386].x * w), int(landmarks[386].y * h))
        pt_bocca = (int(landmarks[13].x * w), int(landmarks[13].y * h))
        
        col_img, col_controlli = st.columns([2, 1])
        
        with col_controlli:
            st.markdown("### Controlli di Modifica")
            st.info("Valori > 0 ingrandiscono, valori < 0 rimpiccioliscono.")
            naso_mod = st.slider("Dimensione Naso", min_value=-0.8, max_value=0.8, value=0.0, step=0.05)
            occhi_mod = st.slider("Dimensione Occhi", min_value=-0.8, max_value=0.8, value=0.0, step=0.05)
            bocca_mod = st.slider("Dimensione Bocca", min_value=-0.8, max_value=0.8, value=0.0, step=0.05)
            
        img_deformed = img_array.copy()
        
        # Applica le deformazioni calcolando il raggio in modo dinamico rispetto alla larghezza (w) dell'immagine
        if naso_mod != 0:
            img_deformed = apply_local_distortion(img_deformed, pt_naso[0], pt_naso[1], radius=max(40, w//10), strength=naso_mod)
        if occhi_mod != 0:
            img_deformed = apply_local_distortion(img_deformed, pt_occhio_sx[0], pt_occhio_sx[1], radius=max(35, w//12), strength=occhi_mod)
            img_deformed = apply_local_distortion(img_deformed, pt_occhio_dx[0], pt_occhio_dx[1], radius=max(35, w//12), strength=occhi_mod)
        if bocca_mod != 0:
            img_deformed = apply_local_distortion(img_deformed, pt_bocca[0], pt_bocca[1], radius=max(45, w//9), strength=bocca_mod)
            
        with col_img:
            st.image(img_deformed, caption="Risultato in Tempo Reale", use_container_width=True)
            
            # Download del risultato
            result_image = Image.fromarray(img_deformed)
            buf = io.BytesIO()
            result_image.save(buf, format="JPEG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="📥 Scarica Immagine Modificata",
                data=byte_im,
                file_name="volto_modificato.jpg",
                mime="image/jpeg"
            )
            
    else:
        st.error("Nessun volto rilevato. Prova con una foto più frontale e ben illuminata.")
