{ nixpkgs ? import <nixpkgs> {} }:

with nixpkgs;

pythonPackages.buildPythonPackage rec {
  name = "lslocks";
  src = ./.;
  buildInputs = [ pkgs.utillinux ];
  pythonPath = [ pythonPackages.psutil ];
  postInstall = ''
    mv "$out/bin/lslocks.py" "$out/bin/lslocks"
  '';
}
