{
  description = "Define development dependencies.";


  inputs = {
    # Which Nix upstream package branch to track
    nixpkgs.url = "nixpkgs/nixos-unstable";
    process-compose-flake.url = "github:Platonic-Systems/process-compose-flake";
    services-flake.url = "github:juspay/services-flake";
  };

  # What results we're going to expose
  outputs = { nixpkgs, process-compose-flake, services-flake, ... }:
    let

      supportedSystems = [ "x86_64-linux" "aarch64-linux" "aarch64-darwin" ];

    in {
      packages = forAllSystems ({ servicesMod, ... }: {
        default = servicesMod.config.outputs.package;
      });

      # Declare what packages we need as a record. The use as a record is
      # needed because, without it, the data contained within can't be
      # referenced in other parts of this file.
      devShells = forAllSystems ({pkgs, servicesMod}: {

        default = pkgs.mkShell rec {
          packages = with pkgs; [
            python39Full
            python310Full
            python311Full
            python312Full
            python313Full
            python314Full
            python3Packages.distlib
            python3Packages.cython
            python3Packages.setuptools
            python3Packages.setuptoolsBuildHook
            python3Packages.wheel
            python3Packages.keyring
            (poetry.override { python3 = pkgs.python3; })
            direnv
            ruff
          ];

          # Getting the library paths needed for Python to be put into
          # LD_LIBRARY_PATH
          pythonldlibpath = "${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.stdenv.cc.cc.lib.outPath}/lib:${pkgs.lib.makeLibraryPath packages}:$NIX_LD_LIBRARY_PATH";

          shellHook = ''
            export LD_LIBRARY_PATH="${pythonldlibpath}"
          '';
        };
      });
    };
}
