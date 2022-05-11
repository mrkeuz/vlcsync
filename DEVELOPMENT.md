# Development

### Build and install
  ```shell
  pip3 install -U .
  ```
  
### Publish
  - Prepare  
     ```shell
    poetry config repositories.testpypi https://test.pypi.org/legacy/
    poetry config pypi-token.testpypi <TOKEN>
    
    poetry config repositories.pypi https://upload.pypi.org/legacy/
    poetry config pypi-token.pypi <TOKEN>
    ```  
  
  - Publish
    ```shell
    poetry publish --build -r testpypi
    
    poetry publish --build -r pypi
    ````
    
### Roadmap:

- [x] Add portable `*.exe` build for Windows
- [ ] Add offsets controlling (web api for cross-platform) for fix unsync video/audio
- [ ] Automatic tune vlc [config](https://wiki.videolan.org/Preferences/#:~:text=Configuration%20File&text=Windows%3A%20%25appdata%25%5Cvlc%5C,%5CApplication%20Data%5Cvlc%5Cvlcrc) file for correct expose
- [ ] Add ability to remote sync (for support external pc)
    - [ ] Via set static vlc addresses i.e. (maybe with port scanner)
    - [ ] Via remote agent, same vlcsyn on remote pc (for simplicity setup).
          Remote vlcsync will watch thier own players, so not need consern and manually expose 
          dynamic vlc ports to local network (and so add firewall rules). You need expose single port from 
          remote agent


