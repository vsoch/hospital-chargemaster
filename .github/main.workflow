workflow "Deploy Dataset Schema" {
  on = "push"
  resolves = ["Extract Dataset Schema"]
}

action "list" {
  uses = "actions/bin/sh@master"
  runs = "ls"
  args = ["/github/workspace"]
}

action "Extract Dataset Schema" {
  needs = ["list"]
  uses = "docker://openschemas/extractors:Dataset"
  secrets = ["GITHUB_TOKEN"]
  env = {
    DATASET_THUMBNAIL = "https://vsoch.github.io/datasets/assets/img/avocado.png"
    DATASET_ABOUT = "Hospital Chargemaster Dinosaur Dataset"
    DATASET_DESCRIPTION = "This is a compiled set of hospital chargemasters for 2019"
  }
  args = ["extract", "--name", "hospital-chargemasters", "--contact", "@vsoch", "--version", "1.0.0", "--deploy"]
}
