use std::fs::File;

use rpt::*;

fn main() -> color_eyre::Result<()> {
    color_eyre::install()?;

    let mut scene = Scene::new();

    // Agregamos una mesa
    scene.add(
        Object::new(
            load_obj(File::open("examples/Pool_Table.obj")?)?
                .scale(&glm::vec3(0.01, 0.01, 0.01))
                .rotate_y(glm::half_pi())
                .translate(&glm::vec3(0.0, -1.0, -10.0)),
        )
        .material(Material::metallic(hex_color(0x994d00), 0.4)),
    );

    scene.add(
        Object::new(
            load_obj(File::open("examples/Pool_Table.obj")?)?
                .scale(&glm::vec3(0.01, 0.01, 0.01))
                .rotate_y(glm::half_pi())
                .translate(&glm::vec3(0.0, -1.0, 10.0)),
        )
        .material(Material::metallic(hex_color(0x994d00), 0.4)),
    );

    scene.add(
        Object::new(
            load_obj(File::open("examples/Pool_Table.obj")?)?
                .scale(&glm::vec3(0.01, 0.01, 0.01))
                .rotate_y(glm::half_pi())
                .translate(&glm::vec3(-10.0, -1.0, -10.0)),
        )
        .material(Material::metallic(hex_color(0x994d00), 0.4)),
    );

    scene.add(
        Object::new(
            load_obj(File::open("examples/Pool_Table.obj")?)?
                .scale(&glm::vec3(0.01, 0.01, 0.01))
                .rotate_y(glm::half_pi())
                .translate(&glm::vec3(10.0, -1.0, -5.0)),
        )
        .material(Material::metallic(hex_color(0x994d00), 0.4)),
    );

    scene.add(
        Object::new(
            load_obj(File::open("examples/Pool_Table.obj")?)?
                .scale(&glm::vec3(0.01, 0.01, 0.01))
                .rotate_y(glm::half_pi())
                .translate(&glm::vec3(-10.0, -1.0, 10.0)),
        )
        .material(Material::metallic(hex_color(0x994d00), 0.4)),
    );

    scene.add(
        Object::new(
            load_obj(File::open("examples/Pool_Table.obj")?)?
                .scale(&glm::vec3(0.01, 0.01, 0.01))
                .rotate_y(glm::half_pi())
                .translate(&glm::vec3(10.0, -1.0, 5.0)),
        )
        .material(Material::metallic(hex_color(0x994d00), 0.4)),
    );

    scene.add(
        Object::new(
            load_obj(File::open("examples/Pool_Table.obj")?)?
                .scale(&glm::vec3(0.01, 0.01, 0.01))
                .rotate_y(glm::half_pi())
                .translate(&glm::vec3(-10.0, -1.0, 0.0)),
        )
        .material(Material::metallic(hex_color(0x994d00), 0.4)),
    );

    scene.add(
        Object::new(
            load_obj(File::open("examples/Pool_Table.obj")?)?
                .scale(&glm::vec3(0.01, 0.01, 0.01))
                .rotate_y(glm::half_pi())
                .translate(&glm::vec3(10.0, -1.0, 0.0)),
        )
        .material(Material::metallic(hex_color(0x994d00), 0.4)),
    );


    // Agregamos un plano que simule un piso
    scene.add(
        Object::new(plane(glm::vec3(0.0, 1.0, 0.0), -1.0))
            .material(Material::diffuse(hex_color(0xff9933))),
    );

    // Plano que simula cielo, para el eje Z
    scene.add(
        Object::new(plane(glm::vec3(0.0, 0.0, 1.0), -1.0)
            .translate(&glm::vec3(0.0, 0.0, -21.0))
        )
            .material(Material::diffuse(hex_color(0xffbf80))),
    );

    // Plano de cielo para el eje X
    scene.add(
        Object::new(plane(glm::vec3(1.0, 0.0, 0.0), -1.0)
            .translate(&glm::vec3(21.0, 0.0, 0.0))
        )
            .material(Material::diffuse(hex_color(0xffbf80))),
    );

    // Agregamos una luz ambiental
    scene.add(Light::Ambient(glm::vec3(0.5, 0.5, 0.5)));

    // Agregamos un punto de luz
    scene.add(Light::Point(
        glm::vec3(60.0, 60.0, 60.0),
        glm::vec3(0.0, 5.0, 0.0),
    ));

    // Seteamos la camara y creamos la imagen, para cambiar la camara, podemos modificar el archivo camera, así es más sencillo :D
    Renderer::new(&scene, Camera::default())
        .width(800)
        .height(800)
        .render()
        .save("fov90_test.png")?;

    Ok(())
}
