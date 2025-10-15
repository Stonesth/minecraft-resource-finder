# Configuration SSH pour la synchronisation automatique

Ce guide vous explique comment configurer le mot de passe SSH pour ne plus avoir à le taper à chaque synchronisation.

## 📋 Prérequis

Pour utiliser l'authentification par mot de passe automatique, vous devez installer `sshpass`.

### Installation de sshpass

#### macOS
```bash
brew install hudochenkov/sshpass/sshpass
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install sshpass
```

## 🔧 Configuration

### 1. Créer le fichier de configuration

Copiez le fichier exemple :
```bash
cp server_config.sh.example server_config.sh
```

### 2. Éditer le mot de passe

Ouvrez `server_config.sh` et remplacez `VOTRE_MOT_DE_PASSE_ICI` par votre vrai mot de passe SSH :

```bash
export VPS_PASSWORD="VotreMotDePasseRéel"
```

### 3. Sécuriser le fichier

Limitez les permissions pour que seul vous puissiez le lire :
```bash
chmod 600 server_config.sh
```

## ✅ Utilisation

Une fois configuré, lancez simplement :
```bash
./sync_from_server.sh
```

Le script détectera automatiquement le fichier `server_config.sh` et utilisera le mot de passe sans vous le demander.

## 🔒 Sécurité

### ⚠️ Important

- ✅ `server_config.sh` est dans `.gitignore` - il ne sera **jamais** committé sur Git
- ✅ Utilisez `chmod 600` pour protéger le fichier
- ❌ Ne partagez **jamais** ce fichier
- ❌ Ne le copiez pas dans des dossiers publics

### Alternative plus sécurisée : Clés SSH

Pour une sécurité maximale, utilisez des clés SSH au lieu de mots de passe :

#### 1. Générer une clé SSH
```bash
ssh-keygen -t ed25519 -C "votre_email@example.com"
```

#### 2. Copier la clé sur le serveur
```bash
ssh-copy-id root@82.25.117.8
```

#### 3. Tester
```bash
ssh root@82.25.117.8
```

Une fois les clés SSH configurées, vous n'aurez plus besoin de `sshpass` ni de `server_config.sh` !

## 🐛 Dépannage

### sshpass n'est pas installé

Si vous voyez ce message :
```
⚠️  Fichier server_config.sh non trouvé - Vous devrez taper le mot de passe
```

Installez `sshpass` (voir ci-dessus) ou configurez des clés SSH.

### Permission denied

Vérifiez que :
1. Le mot de passe dans `server_config.sh` est correct
2. L'utilisateur et l'hôte sont corrects
3. Le serveur accepte l'authentification par mot de passe

### Le fichier n'est pas détecté

Assurez-vous que `server_config.sh` est à la **racine du projet**, pas dans un sous-dossier.
